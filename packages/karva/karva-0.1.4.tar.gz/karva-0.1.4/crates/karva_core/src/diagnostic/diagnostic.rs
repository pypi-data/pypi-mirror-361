use karva_project::path::TestPathError;
use pyo3::prelude::*;

use crate::{
    collection::TestCase,
    diagnostic::{
        render::{DiagnosticInnerDisplay, DisplayDiagnostic},
        sub_diagnostic::SubDiagnostic,
        utils::{get_traceback, get_type_name},
    },
    discovery::DiscoveredModule,
};

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Diagnostic {
    inner: DiagnosticInner,
    sub_diagnostics: Vec<SubDiagnostic>,
}

impl Diagnostic {
    #[must_use]
    pub const fn new(
        message: Option<String>,
        location: Option<String>,
        traceback: Option<String>,
        severity: DiagnosticSeverity,
    ) -> Self {
        Self {
            inner: DiagnosticInner {
                message,
                location,
                traceback,
                severity,
            },
            sub_diagnostics: Vec::new(),
        }
    }

    pub fn add_sub_diagnostics(&mut self, sub_diagnostics: Vec<SubDiagnostic>) {
        self.sub_diagnostics.extend(sub_diagnostics);
    }

    pub fn add_sub_diagnostic(&mut self, sub_diagnostic: SubDiagnostic) {
        self.sub_diagnostics.push(sub_diagnostic);
    }

    #[must_use]
    pub fn sub_diagnostics(&self) -> &[SubDiagnostic] {
        &self.sub_diagnostics
    }

    #[must_use]
    pub fn message(&self) -> Option<&str> {
        self.inner.message.as_deref()
    }

    #[must_use]
    pub const fn severity(&self) -> &DiagnosticSeverity {
        &self.inner.severity
    }

    #[must_use]
    pub const fn display(&self) -> DisplayDiagnostic<'_> {
        DisplayDiagnostic::new(self)
    }

    #[must_use]
    pub const fn inner(&self) -> &DiagnosticInner {
        &self.inner
    }

    pub fn from_py_err(
        py: Python<'_>,
        error: &PyErr,
        message: Option<String>,
        location: Option<String>,
        severity: DiagnosticSeverity,
    ) -> Self {
        Self::new(message, location, Some(get_traceback(py, error)), severity)
    }

    pub fn from_test_fail(
        py: Python<'_>,
        error: &PyErr,
        test_case: &TestCase,
        module: &DiscoveredModule<'_>,
    ) -> Self {
        if error.is_instance_of::<pyo3::exceptions::PyAssertionError>(py) {
            return Self::new(
                None,
                Some(test_case.function().display_with_line(module)),
                Some(get_traceback(py, error)),
                DiagnosticSeverity::Error(DiagnosticErrorType::TestCase(
                    test_case.function().name(),
                    TestCaseDiagnosticType::Fail,
                )),
            );
        }
        Self::from_py_err(
            py,
            error,
            None,
            Some(test_case.function().display_with_line(module)),
            DiagnosticSeverity::Error(DiagnosticErrorType::TestCase(
                test_case.function().name(),
                TestCaseDiagnosticType::Error(get_type_name(py, error)),
            )),
        )
    }

    #[must_use]
    pub fn invalid_path_error(error: &TestPathError) -> Self {
        let path = error.path().display().to_string();
        Self::new(
            Some(format!("{error}")),
            Some(path),
            None,
            DiagnosticSeverity::Error(DiagnosticErrorType::Known("invalid-path".to_string())),
        )
    }

    #[must_use]
    pub const fn unknown_error(message: Option<String>, location: Option<String>) -> Self {
        Self::new(
            message,
            location,
            None,
            DiagnosticSeverity::Error(DiagnosticErrorType::Unknown),
        )
    }

    #[must_use]
    pub fn warning(warning_type: &str, message: Option<String>, location: Option<String>) -> Self {
        Self::new(
            message,
            location,
            None,
            DiagnosticSeverity::Warning(warning_type.to_string()),
        )
    }

    #[must_use]
    pub const fn invalid_fixture(message: Option<String>, location: Option<String>) -> Self {
        Self::new(
            message,
            location,
            None,
            DiagnosticSeverity::Error(DiagnosticErrorType::Fixture(FixtureDiagnosticType::Invalid)),
        )
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DiagnosticInner {
    message: Option<String>,
    location: Option<String>,
    traceback: Option<String>,
    severity: DiagnosticSeverity,
}

impl DiagnosticInner {
    #[cfg(test)]
    #[must_use]
    pub const fn new(
        message: Option<String>,
        location: Option<String>,
        traceback: Option<String>,
        severity: DiagnosticSeverity,
    ) -> Self {
        Self {
            message,
            location,
            traceback,
            severity,
        }
    }

    #[must_use]
    pub const fn display(&self) -> DiagnosticInnerDisplay<'_> {
        DiagnosticInnerDisplay::new(self)
    }

    #[must_use]
    pub fn message(&self) -> Option<&str> {
        self.message.as_deref()
    }

    #[must_use]
    pub fn location(&self) -> Option<&str> {
        self.location.as_deref()
    }

    #[must_use]
    pub fn traceback(&self) -> Option<&str> {
        self.traceback.as_deref()
    }

    #[must_use]
    pub const fn severity(&self) -> &DiagnosticSeverity {
        &self.severity
    }
}

// Diagnostic severity
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DiagnosticSeverity {
    Error(DiagnosticErrorType),
    Warning(String),
}

impl DiagnosticSeverity {
    #[must_use]
    pub const fn is_error(&self) -> bool {
        matches!(self, Self::Error(_))
    }

    #[must_use]
    pub const fn is_test_fail(&self) -> bool {
        matches!(
            self,
            Self::Error(DiagnosticErrorType::TestCase(
                _,
                TestCaseDiagnosticType::Fail
            ))
        )
    }

    #[must_use]
    pub const fn is_test_error(&self) -> bool {
        matches!(
            self,
            Self::Error(DiagnosticErrorType::TestCase(
                _,
                TestCaseDiagnosticType::Error(_)
                    | TestCaseDiagnosticType::Collection(
                        TestCaseCollectionDiagnosticType::FixtureNotFound
                    )
            ))
        )
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DiagnosticErrorType {
    TestCase(String, TestCaseDiagnosticType),
    Fixture(FixtureDiagnosticType),
    Known(String),
    Unknown,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TestCaseDiagnosticType {
    Fail,
    Error(String),
    Collection(TestCaseCollectionDiagnosticType),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TestCaseCollectionDiagnosticType {
    FixtureNotFound,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum FixtureDiagnosticType {
    Invalid,
}

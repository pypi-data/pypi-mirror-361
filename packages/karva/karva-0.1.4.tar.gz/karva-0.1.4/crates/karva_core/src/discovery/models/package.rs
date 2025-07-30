use std::collections::{HashMap, HashSet};

use karva_project::{path::SystemPathBuf, project::Project, utils::module_name};

use crate::{
    discovery::{DiscoveredModule, ModuleType, StringModule, TestFunction},
    extensions::fixtures::{Fixture, HasFixtures, RequiresFixtures},
    utils::Upcast,
};

/// A package represents a single python directory.
pub struct DiscoveredPackage<'proj> {
    path: SystemPathBuf,
    project: &'proj Project,
    modules: HashMap<SystemPathBuf, DiscoveredModule<'proj>>,
    packages: HashMap<SystemPathBuf, DiscoveredPackage<'proj>>,
    configuration_modules: HashSet<SystemPathBuf>,
}

impl<'proj> DiscoveredPackage<'proj> {
    #[must_use]
    pub fn new(path: SystemPathBuf, project: &'proj Project) -> Self {
        Self {
            path,
            project,
            modules: HashMap::new(),
            packages: HashMap::new(),
            configuration_modules: HashSet::new(),
        }
    }

    #[must_use]
    pub const fn path(&self) -> &SystemPathBuf {
        &self.path
    }

    #[must_use]
    pub const fn modules(&self) -> &HashMap<SystemPathBuf, DiscoveredModule<'proj>> {
        &self.modules
    }

    #[must_use]
    pub const fn packages(&self) -> &HashMap<SystemPathBuf, Self> {
        &self.packages
    }

    #[must_use]
    pub fn get_module(&self, path: &SystemPathBuf) -> Option<&DiscoveredModule<'proj>> {
        self.modules.get(path)
    }

    #[must_use]
    pub fn get_package(&self, path: &SystemPathBuf) -> Option<&Self> {
        self.packages.get(path)
    }

    pub fn add_module(&mut self, module: DiscoveredModule<'proj>) {
        if !module.path().starts_with(self.path()) {
            return;
        }

        // If the module path equals our path, add directly to modules
        if *module
            .path()
            .parent()
            .expect("Failed to get parent of module path")
            == **self.path()
        {
            if let Some(existing_module) = self.modules.get_mut(module.path()) {
                existing_module.update(module);
            } else {
                if module.module_type() == ModuleType::Configuration {
                    self.configuration_modules.insert(module.path().clone());
                }
                self.modules.insert(module.path().clone(), module);
            }
            return;
        }

        // Chop off the current path from the start
        let relative_path = module
            .path()
            .strip_prefix(self.path())
            .expect("Failed to strip prefix");
        let components: Vec<_> = relative_path.components().collect();

        if components.is_empty() {
            return;
        }

        let first_component = components[0];
        let intermediate_path = self.path().join(first_component);

        // Try to find existing sub-package and use add_module method
        if let Some(existing_package) = self.packages.get_mut(&intermediate_path) {
            existing_package.add_module(module);
        } else {
            // If not there, create a new one
            let mut new_package = DiscoveredPackage::new(intermediate_path, self.project);
            new_package.add_module(module);
            self.packages
                .insert(new_package.path().clone(), new_package);
        }
    }

    pub fn add_configuration_module(&mut self, module: DiscoveredModule<'proj>) {
        self.configuration_modules.insert(module.path().clone());
        self.add_module(module);
    }

    pub fn add_package(&mut self, package: Self) {
        if !package.path().starts_with(self.path()) {
            return;
        }

        // If the package path equals our path, use update method
        if package.path() == self.path() {
            self.update(package);
            return;
        }

        // Chop off the current path from the start
        let relative_path = package
            .path()
            .strip_prefix(self.path())
            .expect("Failed to strip prefix");
        let components: Vec<_> = relative_path.components().collect();

        if components.is_empty() {
            return;
        }

        let first_component = components[0];
        let intermediate_path = self.path().join(first_component);

        // Try to find existing sub-package and use add_package method
        if let Some(existing_package) = self.packages.get_mut(&intermediate_path) {
            existing_package.add_package(package);
        } else {
            // If not there, create a new one
            let mut new_package = DiscoveredPackage::new(intermediate_path, self.project);
            new_package.add_package(package);
            self.packages
                .insert(new_package.path().clone(), new_package);
        }
    }

    #[must_use]
    pub fn total_test_functions(&self) -> usize {
        let mut total = 0;
        for module in self.modules.values() {
            total += module.total_test_functions();
        }
        for package in self.packages.values() {
            total += package.total_test_functions();
        }
        total
    }

    pub fn update(&mut self, package: Self) {
        for (_, module) in package.modules {
            self.add_module(module);
        }
        for (_, package) in package.packages {
            self.add_package(package);
        }

        for module in package.configuration_modules {
            self.configuration_modules.insert(module);
        }
    }

    #[must_use]
    pub fn test_functions(&self) -> Vec<&TestFunction<'proj>> {
        let mut functions = self.direct_test_functions();

        for sub_package in self.packages.values() {
            functions.extend(sub_package.test_functions());
        }

        functions
    }

    #[must_use]
    pub fn direct_test_functions(&self) -> Vec<&TestFunction<'proj>> {
        let mut functions = Vec::new();

        for module in self.modules.values() {
            functions.extend(module.test_functions());
        }

        functions
    }

    #[must_use]
    pub fn contains_path(&self, path: &SystemPathBuf) -> bool {
        for module in self.modules.values() {
            if module.path() == path {
                return true;
            }
        }
        for package in self.packages.values() {
            if package.path() == path {
                return true;
            }
            if package.contains_path(path) {
                return true;
            }
        }
        false
    }

    // TODO: Rename this
    #[must_use]
    pub fn dependencies(&self) -> Vec<&dyn RequiresFixtures> {
        let mut dependencies: Vec<&dyn RequiresFixtures> = Vec::new();
        let direct_test_functions: Vec<&dyn RequiresFixtures> =
            self.direct_test_functions().upcast();

        for configuration_module in self.configuration_modules() {
            dependencies.extend(configuration_module.dependencies());
        }
        dependencies.extend(direct_test_functions);

        dependencies
    }

    #[must_use]
    pub fn configuration_modules(&self) -> Vec<&DiscoveredModule<'_>> {
        self.configuration_modules
            .iter()
            .filter_map(|path| self.modules.get(path))
            .collect()
    }

    pub fn shrink(&mut self) {
        self.modules.retain(|path, module| {
            if module.is_empty() {
                self.configuration_modules.remove(path);
                false
            } else {
                true
            }
        });

        self.packages.retain(|_, package| !package.is_empty());

        for package in self.packages.values_mut() {
            package.shrink();
        }
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.modules.is_empty() && self.packages.is_empty()
    }

    #[must_use]
    pub fn display(&self) -> StringPackage {
        let mut modules = HashMap::new();
        let mut packages = HashMap::new();

        for module in self.modules().values() {
            if let Some(module_name) = module_name(self.path(), module.path()) {
                modules.insert(module_name, module.into());
            }
        }

        for subpackage in self.packages().values() {
            if let Some(package_name) = module_name(self.path(), subpackage.path()) {
                packages.insert(package_name, subpackage.display());
            }
        }

        StringPackage { modules, packages }
    }
}

impl std::fmt::Debug for DiscoveredPackage<'_> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let string_package: StringPackage = self.display();
        write!(f, "{string_package:?}")
    }
}

impl<'proj> HasFixtures<'proj> for DiscoveredPackage<'proj> {
    fn all_fixtures<'a: 'proj>(
        &'a self,
        test_cases: &[&dyn RequiresFixtures],
    ) -> Vec<&'proj Fixture> {
        let mut fixtures = Vec::new();

        for module in self.configuration_modules() {
            let module_fixtures = module.all_fixtures(test_cases);

            fixtures.extend(module_fixtures);
        }

        fixtures
    }
}

impl<'proj> HasFixtures<'proj> for &'proj DiscoveredPackage<'proj> {
    fn all_fixtures<'a: 'proj>(
        &'a self,
        test_cases: &[&dyn RequiresFixtures],
    ) -> Vec<&'proj Fixture> {
        (*self).all_fixtures(test_cases)
    }
}

#[derive(Debug)]
pub struct StringPackage {
    pub modules: HashMap<String, StringModule>,
    pub packages: HashMap<String, StringPackage>,
}

impl PartialEq for StringPackage {
    fn eq(&self, other: &Self) -> bool {
        self.modules == other.modules && self.packages == other.packages
    }
}

impl Eq for StringPackage {}

#[cfg(test)]
mod tests {
    use karva_project::testing::TestEnv;

    use super::*;

    #[test]
    fn test_update_package() {
        let env = TestEnv::new();

        let tests_dir = env.create_test_dir();

        let project = Project::new(env.cwd(), vec![tests_dir.clone()]);

        let mut package = DiscoveredPackage::new(env.cwd(), &project);

        package.add_module(DiscoveredModule::new(
            &project,
            &tests_dir.join("test_1.py"),
            ModuleType::Test,
        ));

        assert_eq!(
            package.display(),
            StringPackage {
                modules: HashMap::new(),
                packages: HashMap::from([(
                    env.relative_path(&tests_dir).display().to_string(),
                    StringPackage {
                        modules: HashMap::from([(
                            "test_1".to_string(),
                            StringModule::from(&DiscoveredModule::new(
                                &project,
                                &tests_dir.join("test_1.py"),
                                ModuleType::Test
                            ))
                        )]),
                        packages: HashMap::new(),
                    }
                )]),
            }
        );
    }

    #[test]
    fn add_module_different_start_path() {
        let env = TestEnv::new();

        let tests_dir = env.create_test_dir();

        let project = Project::new(env.cwd(), vec![tests_dir.clone()]);

        let mut package = DiscoveredPackage::new(tests_dir, &project);

        let module_dir = env.create_test_dir();

        let module =
            DiscoveredModule::new(&project, &module_dir.join("test_1.py"), ModuleType::Test);

        package.add_module(module);

        assert_eq!(
            package.display(),
            StringPackage {
                modules: HashMap::new(),
                packages: HashMap::new(),
            }
        );
    }

    #[test]
    fn add_module_already_in_package() {
        let env = TestEnv::new();

        let tests_dir = env.create_test_dir();

        let project = Project::new(env.cwd(), vec![tests_dir.clone()]);

        let mut package = DiscoveredPackage::new(env.cwd(), &project);

        let module =
            DiscoveredModule::new(&project, &tests_dir.join("test_1.py"), ModuleType::Test);

        package.add_module(module);

        let module_1 =
            DiscoveredModule::new(&project, &tests_dir.join("test_1.py"), ModuleType::Test);

        package.add_module(module_1);

        assert_eq!(
            package.display(),
            StringPackage {
                modules: HashMap::new(),
                packages: HashMap::from([(
                    env.relative_path(&tests_dir).display().to_string(),
                    StringPackage {
                        modules: HashMap::from([(
                            "test_1".to_string(),
                            StringModule::from(&DiscoveredModule::new(
                                &project,
                                &tests_dir.join("test_1.py"),
                                ModuleType::Test
                            ))
                        )]),
                        packages: HashMap::new(),
                    }
                )]),
            }
        );
    }

    #[test]
    fn add_configuration_module() {
        let env = TestEnv::new();

        let project = Project::new(env.cwd(), vec![env.cwd()]);

        let mut package = DiscoveredPackage::new(env.cwd(), &project);

        let module = DiscoveredModule::new(
            &project,
            &env.cwd().join("conftest.py"),
            ModuleType::Configuration,
        );

        package.add_module(module);

        assert_eq!(
            package.display(),
            StringPackage {
                modules: HashMap::from([(
                    "conftest".to_string(),
                    StringModule::from(&DiscoveredModule::new(
                        &project,
                        &env.cwd().join("conftest.py"),
                        ModuleType::Configuration
                    ))
                )]),
                packages: HashMap::new(),
            }
        );

        assert_eq!(package.configuration_modules().len(), 1);
        assert_eq!(
            package.configuration_modules()[0].path(),
            &env.cwd().join("conftest.py")
        );
    }
}

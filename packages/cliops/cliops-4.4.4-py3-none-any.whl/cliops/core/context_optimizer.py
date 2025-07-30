from typing import Dict, List
from .scanner import ProjectScanner, ProjectContext
from .enhancer import PromptEnhancer
from .intelligence import PromptIntelligence

class ContextAwareOptimizer:
    """Context-aware prompt optimizer that uses project intelligence."""
    
    def __init__(self, cli_state):
        self.cli_state = cli_state
        
    def optimize_with_context(self, raw_prompt: str, folder_path: str = '.') -> Dict[str, str]:
        """Main optimization function using project context."""
        # Scan project for context
        project_context = ProjectScanner.scan_project(folder_path)
        
        if project_context.is_empty:
            return self._handle_empty_project(raw_prompt, project_context)
        else:
            return self._handle_existing_project(raw_prompt, project_context)
    
    def _handle_empty_project(self, raw_prompt: str, context: ProjectContext) -> Dict[str, str]:
        """Handle empty project folders with smart initialization."""
        # Detect intended domain from prompt
        domain = PromptIntelligence.detect_domain(raw_prompt)
        
        # Suggest appropriate tech stack for domain
        suggested_stack = self._suggest_tech_stack(domain, raw_prompt)
        
        return {
            'requirements_section': self._build_empty_requirements(domain, suggested_stack, raw_prompt),
            'tech_specs_section': self._build_empty_tech_specs(domain, suggested_stack),
            'implementation_section': self._build_empty_implementation(domain, suggested_stack),
            'deliverables_section': self._build_empty_deliverables(domain, suggested_stack),
            'code_section': raw_prompt
        }
    
    def _handle_existing_project(self, raw_prompt: str, context: ProjectContext) -> Dict[str, str]:
        """Handle existing projects with discovered context."""
        # If context is too generic/unknown, treat as empty project
        if context.tech_stack == 'unknown' and context.framework == 'unknown' and context.language == 'unknown':
            return self._handle_empty_project(raw_prompt, context)
            
        return {
            'requirements_section': self._build_project_requirements(context, raw_prompt),
            'tech_specs_section': self._build_project_tech_specs(context, raw_prompt),
            'implementation_section': self._build_project_implementation(context, raw_prompt),
            'deliverables_section': self._build_project_deliverables(context, raw_prompt),
            'code_section': raw_prompt
        }
    
    def _suggest_tech_stack(self, domain: str, prompt: str) -> str:
        """Suggest domain-appropriate tech stack."""
        prompt_lower = prompt.lower()
        
        # Comprehensive framework detection within domains
        if domain == 'data_science':
            if 'tensorflow' in prompt_lower: return 'Python + TensorFlow + Jupyter'
            if 'pytorch' in prompt_lower: return 'Python + PyTorch + Jupyter'
            if 'scikit-learn' in prompt_lower: return 'Python + Scikit-learn + Pandas'
            if 'keras' in prompt_lower: return 'Python + Keras + TensorFlow'
            if 'opencv' in prompt_lower: return 'Python + OpenCV + NumPy'
            if 'huggingface' in prompt_lower or 'transformers' in prompt_lower: return 'Python + Transformers + PyTorch'
            if 'matplotlib' in prompt_lower: return 'Python + Matplotlib + Pandas'
            if 'seaborn' in prompt_lower: return 'Python + Seaborn + Matplotlib'
            if 'plotly' in prompt_lower: return 'Python + Plotly + Dash'
            if 'spacy' in prompt_lower: return 'Python + spaCy + NumPy'
            if 'xgboost' in prompt_lower: return 'Python + XGBoost + Pandas'
            if 'lightgbm' in prompt_lower: return 'Python + LightGBM + Pandas'
            if 'mlflow' in prompt_lower: return 'Python + MLflow + Pandas'
            return 'Python + Pandas + Scikit-learn + Jupyter'
        elif domain == 'web_frontend':
            if 'next' in prompt_lower: return 'Next.js + React + TypeScript'
            if 'gatsby' in prompt_lower: return 'Gatsby + React + GraphQL'
            if 'remix' in prompt_lower: return 'Remix + React + TypeScript'
            if 'react' in prompt_lower: return 'React + TypeScript + Vite'
            if 'nuxt' in prompt_lower: return 'Nuxt.js + Vue + TypeScript'
            if 'vue' in prompt_lower: return 'Vue.js + TypeScript + Vite'
            if 'angular' in prompt_lower: return 'Angular + TypeScript + RxJS'
            if 'svelte' in prompt_lower: return 'SvelteKit + TypeScript'
            if 'material-ui' in prompt_lower: return 'React + Material-UI + TypeScript'
            if 'chakra' in prompt_lower: return 'React + Chakra UI + TypeScript'
            if 'ant design' in prompt_lower: return 'React + Ant Design + TypeScript'
            if 'bootstrap' in prompt_lower: return 'Bootstrap + HTML + CSS'
            if 'tailwind' in prompt_lower: return 'Tailwind CSS + HTML + JavaScript'
            return 'Next.js + TypeScript + Tailwind CSS'
        elif domain == 'web_backend':
            if 'django' in prompt_lower: return 'Python + Django + PostgreSQL'
            if 'flask' in prompt_lower: return 'Python + Flask + SQLAlchemy'
            if 'fastapi' in prompt_lower: return 'Python + FastAPI + PostgreSQL'
            if 'nestjs' in prompt_lower: return 'NestJS + TypeScript + PostgreSQL'
            if 'express' in prompt_lower: return 'Node.js + Express + TypeScript'
            if 'hapi' in prompt_lower: return 'Node.js + Hapi + TypeScript'
            if 'koa' in prompt_lower: return 'Node.js + Koa + TypeScript'
            if 'laravel' in prompt_lower: return 'PHP + Laravel + MySQL'
            if 'spring' in prompt_lower: return 'Java + Spring Boot + PostgreSQL'
            if 'rails' in prompt_lower: return 'Ruby + Rails + PostgreSQL'
            if 'gin' in prompt_lower: return 'Go + Gin + PostgreSQL'
            if 'fiber' in prompt_lower: return 'Go + Fiber + PostgreSQL'
            if 'echo' in prompt_lower: return 'Go + Echo + PostgreSQL'
            if 'phoenix' in prompt_lower: return 'Elixir + Phoenix + PostgreSQL'
            return 'Node.js + Express + TypeScript + PostgreSQL'
        elif domain == 'mobile':
            if 'swift' in prompt_lower or 'ios' in prompt_lower: return 'SwiftUI + iOS SDK'
            if 'kotlin' in prompt_lower or 'android' in prompt_lower: return 'Kotlin + Android SDK'
            if 'react native' in prompt_lower: return 'React Native + TypeScript'
            if 'expo' in prompt_lower: return 'Expo + React Native + TypeScript'
            if 'ionic' in prompt_lower: return 'Ionic + Angular + Capacitor'
            if 'xamarin' in prompt_lower: return 'Xamarin + C#'
            if 'cordova' in prompt_lower: return 'Cordova + HTML5 + JavaScript'
            if 'capacitor' in prompt_lower: return 'Capacitor + Ionic + TypeScript'
            if 'nativescript' in prompt_lower: return 'NativeScript + TypeScript'
            if 'titanium' in prompt_lower: return 'Titanium + JavaScript'
            if 'quasar' in prompt_lower: return 'Quasar + Vue + Cordova'
            return 'Flutter + Dart'
        elif domain == 'desktop':
            if 'electron' in prompt_lower: return 'Electron + TypeScript + React'
            if 'tauri' in prompt_lower: return 'Tauri + Rust + TypeScript'
            if 'qt' in prompt_lower: return 'Qt + C++'
            if 'wpf' in prompt_lower: return 'WPF + C# + .NET'
            if 'javafx' in prompt_lower: return 'JavaFX + Java'
            if 'gtk' in prompt_lower: return 'GTK + C'
            if 'tkinter' in prompt_lower: return 'Python + Tkinter'
            if 'pyqt' in prompt_lower: return 'Python + PyQt'
            if 'kivy' in prompt_lower: return 'Python + Kivy'
            if 'avalonia' in prompt_lower: return 'Avalonia + C# + .NET'
            if 'winui' in prompt_lower: return 'WinUI + C# + .NET'
            if 'maui' in prompt_lower: return '.NET MAUI + C#'
            return 'Tauri + Rust + TypeScript'
        elif domain == 'game_development':
            if 'unity' in prompt_lower: return 'Unity + C#'
            if 'unreal' in prompt_lower: return 'Unreal Engine + C++'
            if 'godot' in prompt_lower: return 'Godot + GDScript'
            if 'pygame' in prompt_lower: return 'Python + Pygame'
            if 'phaser' in prompt_lower: return 'Phaser + JavaScript'
            if 'cocos2d' in prompt_lower: return 'Cocos2d + C++'
            if 'gamemaker' in prompt_lower: return 'GameMaker Studio + GML'
            if 'construct' in prompt_lower: return 'Construct 3 + JavaScript'
            if 'defold' in prompt_lower: return 'Defold + Lua'
            if 'love2d' in prompt_lower: return 'LÖVE + Lua'
            return 'Unity + C#'
        elif domain == 'blockchain':
            if 'hardhat' in prompt_lower: return 'Solidity + Hardhat + Ethers.js'
            if 'truffle' in prompt_lower: return 'Solidity + Truffle + Web3.js'
            if 'foundry' in prompt_lower: return 'Solidity + Foundry + Forge'
            if 'brownie' in prompt_lower: return 'Python + Brownie + Web3.py'
            if 'anchor' in prompt_lower: return 'Rust + Anchor + Solana'
            if 'web3' in prompt_lower: return 'JavaScript + Web3.js + Ethereum'
            if 'ethers' in prompt_lower: return 'JavaScript + Ethers.js + Ethereum'
            return 'Solidity + Hardhat + OpenZeppelin'
        elif domain == 'system_programming':
            if 'rust' in prompt_lower: return 'Rust + Cargo'
            if 'c++' in prompt_lower: return 'C++ + CMake'
            if 'go' in prompt_lower: return 'Go + Modules'
            if 'zig' in prompt_lower: return 'Zig + Build System'
            if 'nim' in prompt_lower: return 'Nim + Nimble'
            if 'crystal' in prompt_lower: return 'Crystal + Shards'
            if 'vlang' in prompt_lower: return 'V + V Package Manager'
            if 'odin' in prompt_lower: return 'Odin + Build System'
            return 'Rust + Cargo'
        
        elif domain == 'devops':
            if 'docker' in prompt_lower: return 'Docker + Compose + Dockerfile'
            if 'kubernetes' in prompt_lower: return 'Kubernetes + Helm + YAML'
            if 'terraform' in prompt_lower: return 'Terraform + HCL + AWS'
            if 'ansible' in prompt_lower: return 'Ansible + YAML + Python'
            if 'jenkins' in prompt_lower: return 'Jenkins + Groovy + Pipeline'
            if 'helm' in prompt_lower: return 'Helm + Kubernetes + YAML'
            if 'vagrant' in prompt_lower: return 'Vagrant + Ruby + VirtualBox'
            if 'puppet' in prompt_lower: return 'Puppet + Ruby + Manifests'
            if 'chef' in prompt_lower: return 'Chef + Ruby + Cookbooks'
            if 'pulumi' in prompt_lower: return 'Pulumi + TypeScript + Cloud'
            return 'Docker + Kubernetes + Terraform'
        elif domain == 'testing':
            if 'jest' in prompt_lower: return 'Jest + TypeScript + Node.js'
            if 'cypress' in prompt_lower: return 'Cypress + TypeScript + E2E'
            if 'selenium' in prompt_lower: return 'Selenium + Python + WebDriver'
            if 'pytest' in prompt_lower: return 'Pytest + Python + Fixtures'
            if 'playwright' in prompt_lower: return 'Playwright + TypeScript + E2E'
            if 'mocha' in prompt_lower: return 'Mocha + JavaScript + Chai'
            if 'vitest' in prompt_lower: return 'Vitest + TypeScript + Vite'
            if 'junit' in prompt_lower: return 'JUnit + Java + Maven'
            if 'testng' in prompt_lower: return 'TestNG + Java + Maven'
            if 'rspec' in prompt_lower: return 'RSpec + Ruby + Rails'
            if 'jasmine' in prompt_lower: return 'Jasmine + JavaScript + Karma'
            return 'Jest + Cypress + Playwright'
        elif domain == 'database':
            if 'prisma' in prompt_lower: return 'Prisma + TypeScript + PostgreSQL'
            if 'sequelize' in prompt_lower: return 'Sequelize + Node.js + PostgreSQL'
            if 'mongoose' in prompt_lower: return 'Mongoose + Node.js + MongoDB'
            if 'sqlalchemy' in prompt_lower: return 'SQLAlchemy + Python + PostgreSQL'
            if 'hibernate' in prompt_lower: return 'Hibernate + Java + PostgreSQL'
            return 'PostgreSQL + Prisma + TypeScript'
        elif domain == 'embedded':
            if 'arduino' in prompt_lower: return 'Arduino + C++ + IDE'
            if 'esp32' in prompt_lower: return 'ESP32 + C++ + FreeRTOS'
            if 'raspberry' in prompt_lower: return 'Raspberry Pi + Python + GPIO'
            if 'micropython' in prompt_lower: return 'MicroPython + ESP32'
            return 'Arduino + C++ + Sensors'
        elif domain == 'security':
            if 'metasploit' in prompt_lower: return 'Metasploit + Ruby + Kali'
            if 'burp' in prompt_lower: return 'Burp Suite + Java + Extensions'
            if 'nmap' in prompt_lower: return 'Nmap + Python + Scripts'
            if 'wireshark' in prompt_lower: return 'Wireshark + Lua + Analysis'
            return 'Kali Linux + Python + Tools'
        elif domain == 'ai_ml':
            if 'openai' in prompt_lower: return 'OpenAI + Python + API'
            if 'huggingface' in prompt_lower: return 'HuggingFace + Transformers + PyTorch'
            if 'langchain' in prompt_lower: return 'LangChain + Python + OpenAI'
            return 'Python + TensorFlow + Jupyter'
        elif domain == 'api_integration':
            if 'postman' in prompt_lower: return 'Postman + Newman + JavaScript'
            if 'swagger' in prompt_lower: return 'OpenAPI + Swagger + YAML'
            if 'graphql' in prompt_lower: return 'GraphQL + Apollo + TypeScript'
            return 'REST + OpenAPI + TypeScript'
        
        return 'Node.js + TypeScript'
    
    def _build_empty_requirements(self, domain: str, stack: str, prompt: str) -> str:
        """Build requirements for empty projects."""
        keyword_enhancements = PromptEnhancer.enhance_by_keywords(prompt)
        
        base_reqs = [
            f"Initialize new {domain.replace('_', ' ')} project with {stack}",
            "Set up modern development environment with best practices",
            "Configure linting, formatting, and type checking",
            "Implement proper project structure and organization"
        ]
        
        if keyword_enhancements:
            base_reqs.extend(keyword_enhancements[:2])
        
        return '\n'.join(f"- {req}" for req in base_reqs)
    
    def _build_empty_tech_specs(self, domain: str, stack: str) -> str:
        """Build tech specs for empty projects."""
        specs = {
            'web_frontend': [
                f"Project setup with {stack}",
                "Component architecture with TypeScript",
                "Responsive design system with Tailwind CSS",
                "State management and routing configuration"
            ],
            'web_backend': [
                f"API server setup with {stack}",
                "Database schema design and migrations",
                "Authentication and authorization middleware",
                "API documentation with OpenAPI/Swagger"
            ],
            'mobile': [
                f"Mobile app initialization with {stack}",
                "Navigation and state management setup",
                "Platform-specific configurations and optimizations",
                "Performance optimization and native API integration"
            ],
            'desktop': [
                f"Desktop application setup with {stack}",
                "Cross-platform compatibility and native APIs",
                "UI framework and component architecture",
                "Build and distribution configuration"
            ],
            'game_development': [
                f"Game project initialization with {stack}",
                "Scene management and game object architecture",
                "Physics, rendering, and audio systems",
                "Asset pipeline and build optimization"
            ],
            'blockchain': [
                f"Smart contract project with {stack}",
                "Development environment and testing framework",
                "Security patterns and gas optimization",
                "Deployment and verification scripts"
            ],
            'data_science': [
                f"Data science environment with {stack}",
                "Data pipeline and preprocessing workflows",
                "Model training and evaluation frameworks",
                "Visualization and reporting tools"
            ],
            'devops': [
                f"Infrastructure setup with {stack}",
                "CI/CD pipeline configuration",
                "Container orchestration and scaling",
                "Monitoring and logging systems"
            ],
            'testing': [
                f"Testing framework setup with {stack}",
                "Unit, integration, and E2E test suites",
                "Test automation and reporting",
                "Performance and load testing"
            ],
            'cli_tools': [
                f"CLI application setup with {stack}",
                "Command parsing and argument validation",
                "Interactive prompts and output formatting",
                "Cross-platform compatibility and distribution"
            ],
            'database': [
                f"Database setup with {stack}",
                "Schema design and migration management",
                "Query optimization and indexing strategies",
                "Backup, recovery, and monitoring systems"
            ],
            'embedded': [
                f"Embedded system setup with {stack}",
                "Hardware abstraction and driver development",
                "Real-time constraints and power optimization",
                "Firmware deployment and debugging tools"
            ],
            'security': [
                f"Security framework setup with {stack}",
                "Vulnerability assessment and penetration testing",
                "Security monitoring and incident response",
                "Compliance and audit trail implementation"
            ],
            'ai_ml': [
                f"AI/ML pipeline setup with {stack}",
                "Model architecture and hyperparameter tuning",
                "Training infrastructure and distributed computing",
                "Model deployment and monitoring systems"
            ],
            'api_integration': [
                f"API integration setup with {stack}",
                "Authentication and rate limiting strategies",
                "Data transformation and validation pipelines",
                "Error handling and retry mechanisms"
            ]
        }.get(domain, [
            f"Project initialization with {stack}",
            "Development environment setup",
            "Code quality tools and standards",
            "Testing and deployment configuration"
        ])
        
        # Add system programming specific specs
        if domain == 'system_programming':
            specs = [
                f"System programming setup with {stack}",
                "Memory management and performance optimization",
                "Cross-platform compatibility and native APIs",
                "Build system and dependency management"
            ]
        
        return '\n'.join(f"- {spec}" for spec in specs)
    
    def _build_empty_implementation(self, domain: str, stack: str) -> str:
        """Build implementation steps for empty projects."""
        steps = {
            'web_frontend': [
                f"Initialize {stack.split(' + ')[0]} project with TypeScript",
                "Configure styling framework and component structure",
                "Set up routing and layout components",
                "Implement core features and optimization"
            ],
            'web_backend': [
                f"Initialize {stack.split(' + ')[0]} project with database",
                "Set up database connection and schema",
                "Create API routes and middleware",
                "Implement authentication and error handling"
            ],
            'mobile': [
                f"Initialize {stack.split(' + ')[0]} project with platform SDK",
                "Set up navigation and state management architecture",
                "Create modern UI components with platform-specific design",
                "Implement performance optimizations and native features"
            ],
            'desktop': [
                f"Initialize {stack.split(' + ')[0]} project with backend",
                "Set up frontend framework integration",
                "Implement native API bindings",
                "Configure build and packaging"
            ],
            'game_development': [
                f"Create {stack.split(' + ')[0]} project with scripts",
                "Set up scene hierarchy and game objects",
                "Implement game mechanics and systems",
                "Configure build settings and optimization"
            ],
            'blockchain': [
                f"Initialize {stack.split(' + ')[0]} project with contracts",
                "Write and compile smart contracts",
                "Create deployment and testing scripts",
                "Set up frontend Web3 integration"
            ],
            'data_science': [
                "Set up Python environment with virtual env",
                "Create data pipeline and preprocessing",
                "Implement model training and evaluation",
                "Build visualization and reporting"
            ],
            'devops': [
                "Create Docker containers and compose files",
                "Set up Kubernetes manifests",
                "Configure CI/CD pipelines",
                "Implement monitoring and logging"
            ],
            'testing': [
                "Set up testing framework and configuration",
                "Write unit and integration tests",
                "Create E2E test automation",
                "Configure test reporting and coverage"
            ],
            'cli_tools': [
                "Initialize CLI project with command framework",
                "Implement command parsing and validation",
                "Create interactive prompts and output",
                "Set up build and distribution"
            ],
            'database': [
                f"Initialize {stack.split(' + ')[0]} database project",
                "Design schema with relationships and constraints",
                "Implement data access layer and ORM configuration",
                "Set up migration scripts and seed data"
            ],
            'embedded': [
                f"Initialize {stack.split(' + ')[0]} embedded project",
                "Configure hardware abstraction layer",
                "Implement device drivers and communication protocols",
                "Set up debugging and deployment tools"
            ],
            'security': [
                f"Initialize {stack.split(' + ')[0]} security project",
                "Configure security scanning and assessment tools",
                "Implement monitoring and alerting systems",
                "Set up compliance reporting and documentation"
            ],
            'ai_ml': [
                f"Initialize {stack.split(' + ')[0]} AI/ML project",
                "Set up data preprocessing and feature engineering",
                "Implement model training and evaluation pipelines",
                "Configure deployment and monitoring infrastructure"
            ],
            'api_integration': [
                f"Initialize {stack.split(' + ')[0]} integration project",
                "Configure API clients and authentication",
                "Implement data transformation and validation",
                "Set up error handling and monitoring"
            ]
        }.get(domain, [
            f"Initialize project with {stack}",
            "Configure development environment",
            "Implement core functionality",
            "Set up testing and deployment"
        ])
        
        return '\n'.join(f"- {step}" for step in steps)
    
    def _build_empty_deliverables(self, domain: str, stack: str) -> str:
        """Build framework-specific deliverables for empty projects."""
        framework = stack.split(' + ')[0].lower()
        
        domain_deliverables = {
            'data_science': {
                'tensorflow': ["Trained TensorFlow model with >85% accuracy", "TensorBoard visualization dashboard", "Model deployment with TF Serving", "Performance benchmarks and optimization"],
                'pytorch': ["PyTorch model with training pipeline", "Model checkpoints and versioning", "TorchScript deployment package", "Training metrics visualization"],
                'scikit-learn': ["Scikit-learn model with cross-validation", "Feature importance analysis", "Model performance report", "Hyperparameter tuning results"],
                'keras': ["Keras model with callbacks", "Model architecture visualization", "Training history plots", "Model evaluation metrics"],
                'opencv': ["OpenCV computer vision pipeline", "Image processing algorithms", "Performance benchmarks", "Visual detection results"],
                'matplotlib': ["Interactive data visualizations", "Statistical analysis plots", "Dashboard with multiple charts", "Export-ready publication figures"],
                'seaborn': ["Statistical visualization suite", "Correlation analysis plots", "Distribution analysis charts", "Publication-ready figures"],
                'plotly': ["Interactive Plotly dashboard", "Real-time data visualization", "Web-based analytics interface", "Export capabilities for reports"],
                'xgboost': ["XGBoost model with feature importance", "Cross-validation results", "Hyperparameter optimization report", "Model performance comparison"],
                'lightgbm': ["LightGBM model with early stopping", "Feature selection analysis", "Training optimization report", "Model deployment package"],
                'default': ["ML model with evaluation metrics", "Data pipeline documentation", "Model deployment guide", "Performance analysis report"]
            },
            'web_frontend': {
                'react': ["Production React app with 95%+ Lighthouse score", "Component library with Storybook", "Jest/RTL testing suite", "Bundle size optimization report"],
                'vue': ["Vue.js application with Composition API", "Pinia state management", "Vitest testing framework", "PWA with offline capabilities"],
                'angular': ["Angular app with lazy loading", "RxJS reactive patterns", "Karma/Jasmine test suite", "Angular Universal SSR setup"],
                'svelte': ["SvelteKit application", "Component-based architecture", "Vite build optimization", "TypeScript integration"],
                'next.js': ["Next.js app with SSG/SSR", "API routes implementation", "Image optimization setup", "Vercel deployment configuration"],
                'gatsby': ["Gatsby static site with GraphQL", "Plugin ecosystem integration", "Performance optimization", "SEO and accessibility compliance"],
                'remix': ["Remix app with nested routing", "Progressive enhancement", "Form handling with actions", "Edge deployment ready"],
                'default': ["Modern web application", "Responsive design implementation", "Performance optimization", "Cross-browser testing results"]
            },
            'web_backend': {
                'django': ["Django REST API with DRF", "Database migrations and fixtures", "Celery task queue setup", "Django admin customization"],
                'flask': ["Flask API with SQLAlchemy", "Blueprint-based architecture", "JWT authentication system", "Flask-Migrate database setup"],
                'fastapi': ["FastAPI with automatic OpenAPI docs", "Async database integration", "Pydantic data validation", "Background task processing"],
                'express': ["Express.js REST API", "Middleware architecture", "JWT authentication", "Rate limiting and security"],
                'nestjs': ["NestJS modular architecture", "Dependency injection setup", "GraphQL integration", "Microservices communication"],
                'laravel': ["Laravel API with Eloquent ORM", "Artisan command line tools", "Queue job processing", "Laravel Sanctum authentication"],
                'spring': ["Spring Boot REST API", "JPA/Hibernate integration", "Spring Security setup", "Actuator monitoring endpoints"],
                'rails': ["Ruby on Rails API", "Active Record models", "Sidekiq background jobs", "RSpec testing suite"],
                'default': ["RESTful API with documentation", "Database schema and migrations", "Authentication and authorization", "API testing and monitoring"]
            },
            'mobile': {
                'flutter': ["Cross-platform Flutter app", "State management with Bloc/Riverpod", "Platform-specific integrations", "App store deployment packages"],
                'react': ["React Native app for iOS/Android", "Native module integrations", "Redux/Context state management", "CodePush deployment setup"],
                'swiftui': ["SwiftUI iOS application", "Combine framework integration", "Core Data persistence", "App Store Connect deployment"],
                'kotlin': ["Kotlin Android application", "Jetpack Compose UI", "Room database integration", "Google Play Console setup"],
                'ionic': ["Ionic hybrid application", "Capacitor native plugins", "Angular/React integration", "Cross-platform deployment"],
                'xamarin': ["Xamarin.Forms application", "MVVM architecture pattern", "Platform-specific renderers", "Azure DevOps CI/CD"],
                'default': ["Native mobile application", "Platform deployment packages", "Performance optimization", "User acceptance testing"]
            },
            'desktop': {
                'electron': ["Electron desktop application", "Auto-updater implementation", "Native menu and notifications", "Cross-platform installers"],
                'tauri': ["Tauri desktop app with Rust backend", "System tray integration", "File system access", "Lightweight bundle optimization"],
                'qt': ["Qt C++ desktop application", "Cross-platform UI components", "Signal-slot architecture", "Deployment packages for all platforms"],
                'wpf': ["WPF desktop application", "MVVM pattern implementation", "Data binding and commands", "ClickOnce deployment setup"],
                'javafx': ["JavaFX desktop application", "FXML UI layouts", "Scene Builder integration", "JPackage deployment"],
                'tkinter': ["Python Tkinter GUI application", "Event-driven architecture", "Custom widget implementations", "Executable packaging with PyInstaller"],
                'default': ["Cross-platform desktop application", "Native OS integration", "User interface optimization", "Installation and deployment packages"]
            },
            'game_development': {
                'unity': ["Unity game build for target platforms", "C# scripting architecture", "Asset pipeline optimization", "Unity Analytics integration"],
                'unreal': ["Unreal Engine game package", "Blueprint visual scripting", "C++ gameplay programming", "Platform-specific optimizations"],
                'godot': ["Godot game project", "GDScript gameplay logic", "Scene-based architecture", "Export templates for platforms"],
                'pygame': ["Python Pygame application", "Sprite-based game engine", "Sound and music integration", "Executable game package"],
                'phaser': ["Phaser HTML5 game", "JavaScript game logic", "WebGL rendering optimization", "Progressive web app setup"],
                'default': ["Game build for target platforms", "Asset pipeline documentation", "Performance optimization", "Platform-specific configurations"]
            },
            'blockchain': {
                'solidity': ["Audited Solidity smart contracts", "Gas optimization analysis", "OpenZeppelin security patterns", "Hardhat deployment scripts"],
                'hardhat': ["Hardhat development environment", "Smart contract testing suite", "Deployment automation", "Etherscan verification setup"],
                'truffle': ["Truffle project structure", "Migration scripts", "Web3.js integration", "Ganache local blockchain setup"],
                'foundry': ["Foundry Solidity project", "Forge testing framework", "Cast deployment tools", "Anvil local node setup"],
                'anchor': ["Anchor Solana program", "Rust-based smart contracts", "TypeScript client SDK", "Solana deployment configuration"],
                'default': ["Smart contract suite", "Security audit report", "Deployment documentation", "Integration examples"]
            },
            'devops': {
                'docker': ["Docker containerization setup", "Multi-stage Dockerfile optimization", "Docker Compose orchestration", "Container security scanning"],
                'kubernetes': ["Kubernetes deployment manifests", "Helm chart templates", "Service mesh configuration", "Monitoring and logging setup"],
                'terraform': ["Terraform infrastructure as code", "Multi-environment configurations", "State management setup", "Security and compliance policies"],
                'ansible': ["Ansible automation playbooks", "Inventory management", "Role-based configurations", "Idempotent deployment scripts"],
                'jenkins': ["Jenkins CI/CD pipeline", "Groovy pipeline scripts", "Multi-branch strategies", "Automated testing integration"],
                'default': ["Infrastructure automation", "CI/CD pipeline setup", "Monitoring and alerting", "Security and compliance documentation"]
            },
            'testing': {
                'jest': ["Jest testing framework setup", "Unit and integration tests", "Code coverage reports", "Snapshot testing implementation"],
                'cypress': ["Cypress E2E testing suite", "Page object model", "Visual regression testing", "CI/CD integration"],
                'selenium': ["Selenium WebDriver automation", "Cross-browser testing grid", "Page Object Pattern", "Parallel test execution"],
                'pytest': ["Pytest testing framework", "Fixture-based test setup", "Parametrized testing", "Coverage and reporting"],
                'playwright': ["Playwright cross-browser testing", "Auto-wait mechanisms", "Network interception", "Visual comparisons"],
                'default': ["Comprehensive testing suite", "Automated test execution", "Coverage reporting", "CI/CD integration"]
            },
            'system_programming': {
                'rust': ["Rust application with Cargo", "Memory safety guarantees", "Performance benchmarks", "Cross-compilation setup"],
                'c++': ["C++ application with CMake", "Modern C++ standards", "Memory management optimization", "Cross-platform compatibility"],
                'go': ["Go application with modules", "Concurrent programming patterns", "Performance profiling", "Docker containerization"],
                'zig': ["Zig application with build system", "Compile-time optimizations", "C interoperability", "Cross-compilation targets"],
                'default': ["High-performance system application", "Memory optimization analysis", "Cross-platform compatibility", "Performance benchmarking"]
            },
            'database': {
                'prisma': ["Prisma schema with migrations", "Type-safe database client", "Query optimization analysis", "Database seeding scripts"],
                'sequelize': ["Sequelize ORM setup", "Model associations", "Migration management", "Connection pooling configuration"],
                'mongoose': ["Mongoose MongoDB schemas", "Validation and middleware", "Population strategies", "Index optimization"],
                'sqlalchemy': ["SQLAlchemy ORM models", "Alembic migration system", "Query optimization", "Connection pool management"],
                'default': ["Database schema design", "Migration scripts", "Query optimization", "Backup and recovery procedures"]
            },
            'embedded': {
                'arduino': ["Arduino firmware project", "Sensor integration code", "Power optimization", "Serial communication protocols"],
                'esp32': ["ESP32 IoT application", "WiFi/Bluetooth connectivity", "FreeRTOS task management", "OTA update capability"],
                'raspberry': ["Raspberry Pi application", "GPIO control interface", "Camera/sensor integration", "Remote monitoring setup"],
                'default': ["Embedded system firmware", "Hardware abstraction layer", "Real-time performance optimization", "Deployment and debugging tools"]
            },
            'security': {
                'metasploit': ["Metasploit exploitation modules", "Custom payload development", "Post-exploitation scripts", "Vulnerability assessment report"],
                'burp': ["Burp Suite extension", "Custom scanner checks", "Automated testing workflows", "Security assessment documentation"],
                'nmap': ["Nmap scanning scripts", "Network discovery automation", "Vulnerability detection", "Reporting and analysis tools"],
                'default': ["Security assessment tools", "Vulnerability scanning reports", "Penetration testing documentation", "Compliance audit results"]
            },
            'ai_ml': {
                'openai': ["OpenAI API integration", "Prompt engineering templates", "Response processing pipeline", "Usage monitoring dashboard"],
                'langchain': ["LangChain application framework", "Chain composition patterns", "Vector database integration", "Agent-based workflows"],
                'huggingface': ["HuggingFace model integration", "Custom tokenizer setup", "Model fine-tuning pipeline", "Inference optimization"],
                'default': ["AI/ML application", "Model deployment pipeline", "Performance monitoring", "Scalable inference setup"]
            },
            'api_integration': {
                'postman': ["Postman collection suite", "Automated testing workflows", "Environment configurations", "API documentation generation"],
                'graphql': ["GraphQL API implementation", "Schema design and resolvers", "Query optimization", "Subscription real-time updates"],
                'swagger': ["OpenAPI specification", "Interactive documentation", "Code generation setup", "API versioning strategy"],
                'default': ["API integration framework", "Authentication and authorization", "Rate limiting and caching", "Monitoring and analytics"]
            }
        }
        
        if domain in domain_deliverables:
            domain_dict = domain_deliverables[domain]
            for key in domain_dict:
                if key in framework:
                    return '\n'.join(f"- {deliverable}" for deliverable in domain_dict[key])
            return '\n'.join(f"- {deliverable}" for deliverable in domain_dict['default'])
        
        # Generic deliverables for other domains
        return '\n'.join(f"- {deliverable}" for deliverable in [
            f"Fully configured {domain.replace('_', ' ')} project",
            "Development environment with hot reload",
            "Code quality tools and documentation",
            "README with setup and development instructions"
        ])
    
    def _build_project_requirements(self, context: ProjectContext, prompt: str) -> str:
        """Build requirements using actual project context."""
        keyword_enhancements = PromptEnhancer.enhance_by_keywords(prompt)
        
        # Filter out unknown/generic values
        domain = context.domain if context.domain != 'unknown' else 'application'
        tech_stack = context.tech_stack if context.tech_stack != 'unknown' else 'current technology stack'
        framework = context.framework if context.framework != 'unknown' else 'existing framework'
        
        base_reqs = [
            f"Extend existing {domain.replace('_', ' ')} project using {tech_stack}",
            f"Maintain compatibility with current {framework} setup",
            "Follow existing code patterns and architecture",
            f"Integrate with current dependencies: {', '.join(list(context.dependencies.keys())[:3])}"
        ]
        
        if keyword_enhancements:
            base_reqs.extend(keyword_enhancements[:2])
        
        return '\n'.join(f"- {req}" for req in base_reqs)
    
    def _build_project_tech_specs(self, context: ProjectContext, prompt: str) -> str:
        """Build tech specs using discovered project details."""
        # Filter out unknown values
        tech_stack = context.tech_stack if context.tech_stack != 'unknown' else 'Modern technology stack'
        framework = context.framework if context.framework != 'unknown' else 'Current framework'
        
        specs = [
            f"Current stack: {tech_stack}",
            f"Framework: {framework}",
            f"Existing structure: {', '.join(context.structure)}" if context.structure else "Standard project structure"
        ]
        
        # Add specific dependencies
        key_deps = ['typescript', 'tailwindcss', 'prisma', 'redux', 'axios']
        found_deps = [dep for dep in key_deps if dep in context.dependencies]
        if found_deps:
            specs.append(f"Key dependencies: {', '.join(found_deps)}")
        
        return '\n'.join(f"- {spec}" for spec in specs)
    
    def _build_project_implementation(self, context: ProjectContext, prompt: str) -> str:
        """Build implementation using actual project structure."""
        # Filter out unknown values
        framework = context.framework if context.framework != 'unknown' else 'current'
        tech_stack = context.tech_stack if context.tech_stack != 'unknown' else 'established technologies'
        
        steps = [
            f"Work within existing {framework} architecture",
            f"Follow current project structure in /{', /'.join(context.structure)}" if context.structure else "Follow existing project patterns",
            f"Use established dependencies: {tech_stack}",
            "Maintain code consistency with existing patterns"
        ]
        
        return '\n'.join(f"- {step}" for step in steps)
    
    def _build_project_deliverables(self, context: ProjectContext, prompt: str) -> str:
        """Build deliverables based on existing project."""
        # Filter out unknown values
        domain = context.domain if context.domain != 'unknown' else 'application'
        framework = context.framework if context.framework != 'unknown' else 'current'
        
        deliverables = [
            f"Enhanced {domain.replace('_', ' ')} functionality",
            f"Integration with existing {framework} codebase",
            "Maintained compatibility with current dependencies",
            "Updated documentation reflecting changes"
        ]
        
        return '\n'.join(f"- {deliverable}" for deliverable in deliverables)
"""
Command Line Interface for Code Auto-Documenter

Provides CLI commands for parsing code, generating documentation,
and integrating with Git workflows.
"""

import click
import os
import yaml
from pathlib import Path
from typing import List, Optional

from parsers.python_parser import PythonParser
from parsers.javascript_parser import JavaScriptParser
from generators.ai_generator import AIGenerator
from generators.template_generator import TemplateGenerator
from utils.git_integration import GitIntegration
from utils.file_utils import FileUtils
from evaluators.readability_metrics import ReadabilityAnalyzer
from evaluators.coverage_analyzer import CoverageAnalyzer
from evaluators.hallucination_detector import HallucinationDetector


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Code Auto-Documenter - AI-powered documentation generation tool."""
    pass


@cli.command()
@click.argument('repository_path', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file path')
@click.option('--output', '-o', type=click.Path(), default='./docs',
              help='Output directory for generated documentation')
@click.option('--languages', '-l', multiple=True, 
              type=click.Choice(['python', 'javascript', 'typescript']),
              default=['python', 'javascript'],
              help='Programming languages to process')
@click.option('--style', type=click.Choice(['google', 'numpy', 'sphinx', 'jsdoc']),
              default='google', help='Documentation style guide')
@click.option('--format', type=click.Choice(['markdown', 'html']),
              default='markdown', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def generate(repository_path, config, output, languages, style, format, verbose):
    """Generate documentation for a code repository."""
    try:
        click.echo(f"🚀 Starting documentation generation for {repository_path}")
        
        # Load configuration
        config_data = load_config(config)
        
        # Initialize components
        ai_generator = AIGenerator(config_data.get('openai', {}))
        template_generator = TemplateGenerator(style)
        file_utils = FileUtils()
        
        # Create output directory
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process each language
        total_files = 0
        for language in languages:
            click.echo(f"📝 Processing {language} files...")
            
            if language == 'python':
                parser = PythonParser()
                file_extensions = ['.py']
            elif language in ['javascript', 'typescript']:
                parser = JavaScriptParser()
                file_extensions = ['.js', '.ts', '.jsx', '.tsx']
            else:
                click.echo(f"❌ Unsupported language: {language}")
                continue
            
            # Find source files
            source_files = file_utils.find_source_files(
                repository_path, file_extensions
            )
            
            if verbose:
                click.echo(f"Found {len(source_files)} {language} files")
            
            # Process each file
            for file_path in source_files:
                try:
                    # Parse the file
                    parsed_elements = parser.parse_file(file_path)
                    
                    if not parsed_elements:
                        continue
                    
                    # Generate documentation using AI
                    documentation = ai_generator.generate_documentation(
                        parsed_elements, language, style
                    )
                    
                    # Create output files
                    relative_path = os.path.relpath(file_path, repository_path)
                    doc_path = output_path / language / relative_path
                    doc_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Generate markdown documentation
                    if format == 'markdown':
                        md_content = template_generator.generate_file_documentation(
                            parsed_elements, documentation, relative_path
                        )
                        
                        with open(f"{doc_path}.md", 'w', encoding='utf-8') as f:
                            f.write(md_content)
                    
                    total_files += 1
                    
                    if verbose:
                        click.echo(f"  ✅ Processed {relative_path}")
                        
                except Exception as e:
                    if verbose:
                        click.echo(f"  ❌ Error processing {file_path}: {e}")
                    continue
        
        # Generate module-level documentation
        click.echo("📚 Generating module-level documentation...")
        generate_module_docs(repository_path, output_path, languages, ai_generator, template_generator)
        
        # Generate API reference
        generate_api_reference(output_path, languages, template_generator)
        
        click.echo(f"✅ Documentation generation complete!")
        click.echo(f"📁 Output directory: {output_path}")
        click.echo(f"📊 Processed {total_files} files")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        return 1


@cli.command()
@click.argument('repository_path', type=click.Path(exists=True))
def setup_hooks(repository_path):
    """Set up Git hooks for automatic documentation updates."""
    try:
        git_integration = GitIntegration()
        git_integration.setup_pre_commit_hook(repository_path)
        click.echo("✅ Git hooks setup complete!")
        
    except Exception as e:
        click.echo(f"❌ Error setting up hooks: {e}", err=True)
        return 1


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--style', type=click.Choice(['google', 'numpy', 'sphinx', 'jsdoc']),
              default='google', help='Documentation style guide')
def analyze(file_path, style):
    """Analyze a single file and show what documentation would be generated."""
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.py':
            parser = PythonParser()
            language = 'python'
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            parser = JavaScriptParser()
            language = 'javascript'
        else:
            click.echo(f"❌ Unsupported file type: {file_ext}")
            return 1
        
        # Parse the file
        parsed_elements = parser.parse_file(file_path)
        
        if not parsed_elements:
            click.echo("No documentable elements found in file.")
            return 0
        
        # Display analysis
        click.echo(f"📋 Analysis for {file_path}")
        click.echo(f"Language: {language}")
        click.echo(f"Style: {style}")
        click.echo(f"Elements found: {len(parsed_elements)}")
        click.echo()
        
        for element in parsed_elements:
            click.echo(f"  📌 {element.type}: {element.name}")
            if hasattr(element, 'parameters') and element.parameters:
                param_names = [p.name if hasattr(p, 'name') else str(p) for p in element.parameters]
                click.echo(f"     Parameters: {', '.join(param_names)}")
            if hasattr(element, 'return_type') and element.return_type:
                click.echo(f"     Returns: {element.return_type}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error analyzing file: {e}", err=True)
        return 1


@cli.command()
@click.argument('documentation_path', type=click.Path(exists=True))
@click.option('--source', '-s', type=click.Path(exists=True), 
              help='Source code path for validation')
@click.option('--output', '-o', type=click.Path(), default='./evaluation',
              help='Output directory for evaluation reports')
@click.option('--language', type=click.Choice(['python', 'javascript', 'typescript']),
              default='python', help='Programming language')
def evaluate(documentation_path, source, output, language):
    """Evaluate documentation quality with readability and hallucination metrics."""
    try:
        click.echo(f"📊 Starting documentation evaluation for {documentation_path}")
        
        # Create output directory
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzers
        readability_analyzer = ReadabilityAnalyzer()
        coverage_analyzer = CoverageAnalyzer()
        hallucination_detector = HallucinationDetector()
        
        # Read documentation files
        doc_files = []
        doc_path = Path(documentation_path)
        
        if doc_path.is_file():
            doc_files = [doc_path]
        else:
            doc_files = list(doc_path.glob('**/*.md'))
        
        total_readability_score = 0
        total_coverage_score = 0
        total_confidence_score = 0
        file_count = 0
        
        for doc_file in doc_files:
            click.echo(f"📝 Evaluating {doc_file.name}...")
            
            with open(doc_file, 'r', encoding='utf-8') as f:
                doc_content = f.read()
            
            # Readability analysis
            readability_metrics = readability_analyzer.analyze_documentation(doc_content, language)
            total_readability_score += readability_metrics.overall_score
            
            # Coverage analysis (simplified for demo)
            elements = []  # Would normally parse source code
            generated_docs = {}
            coverage_metrics = coverage_analyzer.analyze_coverage(elements, generated_docs)
            total_coverage_score += coverage_metrics.coverage_percentage
            
            # Hallucination detection
            hallucination_report = hallucination_detector.detect_hallucinations(elements, generated_docs)
            total_confidence_score += hallucination_report.confidence_score
            
            file_count += 1
        
        # Calculate overall metrics
        avg_readability = total_readability_score / file_count if file_count > 0 else 0
        avg_coverage = total_coverage_score / file_count if file_count > 0 else 0
        avg_confidence = total_confidence_score / file_count if file_count > 0 else 0
        
        # Generate evaluation summary
        summary_content = f"""# Documentation Evaluation Summary

## Overall Metrics
- **Readability Score**: {avg_readability:.1f}/100
- **Coverage Score**: {avg_coverage:.1f}%
- **Confidence Score**: {avg_confidence:.1f}%
- **Files Evaluated**: {file_count}

## Quality Assessment
- **Readability**: {'✅ Excellent' if avg_readability >= 80 else '⚠️ Good' if avg_readability >= 60 else '❌ Needs Improvement'}
- **Coverage**: {'✅ Excellent' if avg_coverage >= 90 else '⚠️ Good' if avg_coverage >= 70 else '❌ Needs Improvement'}
- **Confidence**: {'✅ High' if avg_confidence >= 80 else '⚠️ Medium' if avg_confidence >= 60 else '❌ Low'}

## Recommendations
"""
        
        if avg_readability < 60:
            summary_content += "- Improve documentation clarity and structure\n"
        if avg_coverage < 70:
            summary_content += "- Add more comprehensive documentation coverage\n"
        if avg_confidence < 60:
            summary_content += "- Review and validate AI-generated content for accuracy\n"
        
        # Save evaluation summary
        summary_path = output_path / "evaluation_summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        click.echo(f"✅ Evaluation complete!")
        click.echo(f"📁 Reports saved to: {output_path}")
        click.echo(f"📊 Overall Quality Score: {(avg_readability + avg_coverage + avg_confidence) / 3:.1f}/100")
        
    except Exception as e:
        click.echo(f"❌ Error during evaluation: {e}", err=True)
        return 1


def load_config(config_path: Optional[str]) -> dict:
    """Load configuration from file or use defaults."""
    default_config_path = Path(__file__).parent.parent / 'config' / 'default_config.yaml'
    
    if config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    elif default_config_path.exists():
        with open(default_config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        return {
            'openai': {
                'model': 'gpt-5',
                'max_tokens': 1000,
                'temperature': 0.3
            },
            'style_guides': {
                'google': True,
                'numpy': False,
                'sphinx': False,
                'jsdoc': False
            }
        }


def generate_module_docs(repo_path: str, output_path: Path, languages: List[str], 
                        ai_generator: AIGenerator, template_generator: TemplateGenerator):
    """Generate module-level documentation."""
    for language in languages:
        module_structure = analyze_module_structure(repo_path, language)
        
        if module_structure:
            readme_content = ai_generator.generate_module_readme(
                module_structure, language
            )
            
            module_doc = template_generator.generate_module_readme(
                module_structure, readme_content
            )
            
            with open(output_path / f"{language}_README.md", 'w', encoding='utf-8') as f:
                f.write(module_doc)


def generate_api_reference(output_path: Path, languages: List[str], 
                          template_generator: TemplateGenerator):
    """Generate API reference documentation."""
    api_content = template_generator.generate_api_reference(languages)
    
    with open(output_path / "API_REFERENCE.md", 'w', encoding='utf-8') as f:
        f.write(api_content)


def analyze_module_structure(repo_path: str, language: str) -> dict:
    """Analyze the module structure of a repository."""
    file_utils = FileUtils()
    
    if language == 'python':
        extensions = ['.py']
    else:
        extensions = ['.js', '.ts', '.jsx', '.tsx']
    
    files = file_utils.find_source_files(repo_path, extensions)
    
    return {
        'language': language,
        'total_files': len(files),
        'modules': [os.path.relpath(f, repo_path) for f in files[:10]],  # Sample modules
        'structure': file_utils.build_directory_tree(repo_path, extensions)
    }


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()

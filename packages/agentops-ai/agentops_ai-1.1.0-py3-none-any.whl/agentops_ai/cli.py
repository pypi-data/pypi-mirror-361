"""
AgentOps CLI - AI-powered QA co-pilot for requirements-driven test automation.
"""

import click
import os
import sys
from typing import List, Optional
from .workflow import AgentOpsWorkflow
from .requirements_clarification import RequirementsClarificationEngine


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AgentOps - AI-powered QA co-pilot for requirements-driven test automation."""
    pass


@cli.command()
@click.argument('source_files', nargs=-1)
@click.option('--approval-mode', '-a', default='fast', 
              type=click.Choice(['fast', 'manual', 'auto']),
              help='Approval mode for requirements')
def run(source_files, approval_mode):
    """Run the complete AgentOps workflow on source files."""
    if not source_files:
        click.echo("❌ No source files specified")
        return
    
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.run_multi_agent_workflow(list(source_files), approval_mode)
        
        if result["success"]:
            click.echo("✅ Workflow completed successfully!")
            click.echo(f"📊 Requirements processed: {result.get('requirements_processed', 0)}")
            click.echo(f"🧪 Tests generated: {len(result.get('tests_generated', []))}")
            click.echo(f"📋 Traceability matrix: {result.get('traceability_file', 'N/A')}")
        else:
            click.echo(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.argument('source_files', nargs=-1)
def extract_requirements(source_files):
    """Extract requirements from source files."""
    if not source_files:
        click.echo("❌ No source files specified")
        return
    
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.extract_requirements_from_files(list(source_files))
        
        if result["success"]:
            click.echo("✅ Requirements extracted successfully!")
            click.echo(f"📊 Requirements found: {result.get('requirements_count', 0)}")
        else:
            click.echo(f"❌ Failed to extract requirements: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.argument('source_files', nargs=-1)
def generate_tests(source_files):
    """Generate tests from requirements."""
    if not source_files:
        click.echo("❌ No source files specified")
        return
    
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.generate_tests_from_files(list(source_files))
        
        if result["success"]:
            click.echo("✅ Tests generated successfully!")
            click.echo(f"🧪 Test files created: {result.get('test_files_created', 0)}")
        else:
            click.echo(f"❌ Failed to generate tests: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def run_tests():
    """Run all generated tests."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.run_all_tests()
        
        if result["success"]:
            click.echo("✅ Tests completed!")
            click.echo(f"📊 Tests run: {result.get('tests_run', 0)}")
            click.echo(f"✅ Passed: {result.get('passed', 0)}")
            click.echo(f"❌ Failed: {result.get('failed', 0)}")
        else:
            click.echo(f"❌ Test execution failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.option('--format', '-f', default='markdown',
              type=click.Choice(['markdown', 'html', 'json']),
              help='Output format for traceability matrix')
def traceability(format):
    """Generate traceability matrix."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.generate_traceability_matrix(format)
        
        if result["success"]:
            click.echo("✅ Traceability matrix generated!")
            click.echo(f"📄 Output file: {result.get('file_path', 'N/A')}")
        else:
            click.echo(f"❌ Failed to generate traceability matrix: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.option('--format', '-f', default='gherkin',
              type=click.Choice(['gherkin', 'markdown']),
              help='Export format for requirements')
def export_requirements(format):
    """Export requirements to file."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.export_requirements(format)
        
        if result["success"]:
            click.echo("✅ Requirements exported successfully!")
            click.echo(f"📄 Output file: {result.get('file_path', 'N/A')}")
        else:
            click.echo(f"❌ Failed to export requirements: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.argument('requirement_id')
@click.argument('clarification')
@click.option('--method', '-m', default='manual',
              type=click.Choice(['manual', 'auto']),
              help='Update method for clarification')
def clarify_requirement(requirement_id, clarification, method):
    """Clarify a specific requirement."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.clarify_requirements(requirement_id, clarification, method)
        
        if result["success"]:
            click.echo("✅ Requirement clarified successfully!")
            click.echo(f"🆔 Requirement ID: {requirement_id}")
            click.echo(f"📝 Clarification: {clarification}")
        else:
            click.echo(f"❌ Failed to clarify requirement: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def analyze_failures():
    """Analyze test failures and suggest clarifications."""
    try:
        engine = RequirementsClarificationEngine()
        result = engine.analyze_test_failures()
        
        if result["success"]:
            click.echo("✅ Failure analysis completed!")
            click.echo(f"🔍 Failures analyzed: {result.get('failures_analyzed', 0)}")
            click.echo(f"💡 Clarifications suggested: {result.get('clarifications_suggested', 0)}")
        else:
            click.echo(f"❌ Failed to analyze failures: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def audit_history():
    """Show requirements clarification audit history."""
    try:
        engine = RequirementsClarificationEngine()
        audits = engine.get_audit_history()
        
        if audits:
            click.echo("📋 Requirements Clarification Audit History")
            click.echo("=" * 60)
            
            for audit in audits:
                click.echo(f"🆔 {audit.audit_id}")
                click.echo(f"📝 Requirement: {audit.requirement_id}")
                click.echo(f"🔧 Method: {audit.update_method}")
                click.echo(f"📅 Timestamp: {audit.timestamp}")
                click.echo(f"💡 Reason: {audit.clarification_reason}")
                click.echo("-" * 40)
        else:
            click.echo("📋 No audit history found")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


# Version Management Commands

@cli.command()
@click.option('--description', '-d', required=True, help='Description of this version')
def create_version(description):
    """Create a manual version snapshot of all documentation."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.create_manual_version(description)
        
        if result["success"]:
            click.echo(f"✅ Version created: {result['version_id']}")
            click.echo(f"📝 Description: {description}")
        else:
            click.echo(f"❌ Failed to create version: {result['error']}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def list_versions():
    """List all available version snapshots."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.list_versions()
        
        if result["success"]:
            versions = result["versions"]
            if not versions:
                click.echo("📋 No versions found")
                return
            
            click.echo("📋 Available Versions:")
            click.echo("=" * 80)
            
            for version in versions:
                click.echo(f"🆔 {version['version_id']}")
                click.echo(f"📅 {version['timestamp']}")
                click.echo(f"📝 {version['description']}")
                click.echo(f"🔧 Trigger: {version['trigger']}")
                click.echo(f"📊 Requirements: {version['requirements_count']}, Tests: {version['tests_count']}, Clarifications: {version['clarifications_count']}")
                click.echo("-" * 40)
        else:
            click.echo(f"❌ Failed to list versions: {result['error']}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.argument('version_id')
def restore_version(version_id):
    """Restore a specific version snapshot."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.restore_version(version_id)
        
        if result["success"]:
            click.echo(f"✅ Version {version_id} restored successfully")
            click.echo("📁 Files restored:")
            click.echo("   - requirements.gherkin")
            click.echo("   - requirements.md")
            click.echo("   - tests/")
            click.echo("   - traceability_matrix.md")
        else:
            click.echo(f"❌ Failed to restore version {version_id}: {result['error']}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.argument('version1_id')
@click.argument('version2_id')
def compare_versions(version1_id, version2_id):
    """Compare two version snapshots."""
    try:
        workflow = AgentOpsWorkflow()
        result = workflow.compare_versions(version1_id, version2_id)
        
        if result["success"]:
            comparison = result["comparison"]
            click.echo(f"📊 Comparing {version1_id} vs {version2_id}")
            click.echo("=" * 60)
            
            differences = comparison["differences"]
            click.echo(f"📈 Requirements: {differences['requirements_count']:+d}")
            click.echo(f"🧪 Tests: {differences['tests_count']:+d}")
            click.echo(f"💡 Clarifications: {differences['clarifications_count']:+d}")
            
            if differences["new_files"]:
                click.echo(f"📁 New files: {', '.join(differences['new_files'])}")
            if differences["removed_files"]:
                click.echo(f"🗑️ Removed files: {', '.join(differences['removed_files'])}")
        else:
            click.echo(f"❌ Failed to compare versions: {result['error']}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def version_info():
    """Show information about the current version system."""
    try:
        workflow = AgentOpsWorkflow()
        versions = workflow.version_manager.list_versions()
        
        click.echo("📋 Version System Information")
        click.echo("=" * 50)
        click.echo(f"📁 Versions directory: {workflow.version_manager.versions_dir}")
        click.echo(f"📊 Total versions: {len(versions)}")
        
        if versions:
            latest = versions[0]  # First in list is most recent
            click.echo(f"🆕 Latest version: {latest.version_id}")
            click.echo(f"📅 Latest timestamp: {latest.timestamp}")
            click.echo(f"📝 Latest description: {latest.description}")
        
        # Check if latest symlink exists
        latest_link = os.path.join(workflow.version_manager.versions_dir, "latest")
        if os.path.exists(latest_link):
            click.echo(f"🔗 Latest symlink: {os.path.realpath(latest_link)}")
        else:
            click.echo("🔗 Latest symlink: Not found")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


if __name__ == '__main__':
    cli() 
#!/usr/bin/env python3
"""
BrainCargo Comprehensive Test Runner
Combines all test suites for complete validation
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

# ANSI color codes for pretty output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(message):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}🧪 {message}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️ {message}{Colors.END}")

def run_command(command, description, timeout=300):
    """Run a command and return success status"""
    print_info(f"Running: {description}")
    print_info(f"Command: {command}")
    
    try:
        # Run the command
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if process.returncode == 0:
            print_success(f"{description} completed successfully")
            if process.stdout:
                # Print last few lines of output for context
                lines = process.stdout.strip().split('\n')
                if len(lines) > 5:
                    print_info("Output (last 5 lines):")
                    for line in lines[-5:]:
                        print(f"  {line}")
                else:
                    print_info("Output:")
                    print(process.stdout)
            return True
        else:
            print_error(f"{description} failed (exit code: {process.returncode})")
            if process.stderr:
                print_error("Error output:")
                print(process.stderr)
            if process.stdout:
                print_info("Standard output:")
                print(process.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print_error(f"{description} failed with exception: {str(e)}")
        return False

def check_prerequisites():
    """Check if required tools are available"""
    print_header("Prerequisites Check")
    
    checks = []
    
    # Check Python
    try:
        import yaml
        print_success("PyYAML available")
        checks.append(True)
    except ImportError:
        print_error("PyYAML not available - install with: pip install PyYAML")
        checks.append(False)
    
    # Check Docker
    docker_check = run_command("docker --version", "Docker availability check", timeout=10)
    checks.append(docker_check)
    
    # Check Docker Compose
    compose_check = run_command("docker-compose --version", "Docker Compose availability check", timeout=10)
    checks.append(compose_check)
    
    # Check if required files exist
    required_files = [
        'config/pipeline.yaml',
        'docker-compose.yml',
        'test_local.py',
        'test_pipeline.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Required file exists: {file_path}")
            checks.append(True)
        else:
            print_error(f"Required file missing: {file_path}")
            checks.append(False)
    
    all_good = all(checks)
    if all_good:
        print_success("All prerequisites met")
    else:
        print_error("Some prerequisites are missing")
    
    return all_good

def test_pipeline_architecture():
    """Test the pipeline architecture without running the service"""
    print_header("Pipeline Architecture Tests")
    
    # Test pipeline configuration
    config_test = run_command(
        "python test_local.py --pipeline",
        "Pipeline configuration and architecture test",
        timeout=60
    )
    
    # Test pipeline unit tests
    unit_test = run_command(
        "python test_pipeline.py",
        "Pipeline unit tests",
        timeout=120
    )
    
    return config_test and unit_test

def test_service_integration():
    """Test the service with Docker integration"""
    print_header("Service Integration Tests")
    
    print_info("Starting Docker Compose service...")
    
    # Clean up any existing containers
    cleanup = run_command(
        "docker-compose down --remove-orphans",
        "Cleanup existing containers",
        timeout=30
    )
    
    # Start the service
    start_service = run_command(
        "docker-compose up --build -d",
        "Start BrainCargo Blog Service",
        timeout=300
    )
    
    if not start_service:
        print_error("Failed to start service")
        return False
    
    # Wait for service to be ready
    print_info("Waiting for service to be ready...")
    time.sleep(10)
    
    # Run service tests
    service_test = run_command(
        "python test_local.py",
        "Service integration tests",
        timeout=300
    )
    
    # Stop the service
    stop_service = run_command(
        "docker-compose down",
        "Stop BrainCargo Blog Service",
        timeout=60
    )
    
    return service_test

def test_complete_workflow():
    """Test the complete workflow end-to-end"""
    print_header("Complete Workflow Test")
    
    # This would test the actual blog generation workflow
    # For now, we'll use the existing comprehensive test
    return run_command(
        "python test_local.py --webhook",
        "End-to-end blog generation test",
        timeout=120
    )

def cleanup_environment():
    """Clean up test environment"""
    print_header("Environment Cleanup")
    
    cleanup_commands = [
        ("docker-compose down --volumes --remove-orphans", "Stop and remove all containers"),
        ("docker system prune -f", "Clean up Docker resources")
    ]
    
    results = []
    for command, description in cleanup_commands:
        result = run_command(command, description, timeout=60)
        results.append(result)
    
    return all(results)

def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description="BrainCargo Comprehensive Test Runner")
    parser.add_argument('--quick', action='store_true', help='Run only pipeline tests (no Docker)')
    parser.add_argument('--service-only', action='store_true', help='Run only service integration tests')
    parser.add_argument('--cleanup', action='store_true', help='Clean up environment only')
    parser.add_argument('--no-cleanup', action='store_true', help='Skip cleanup after tests')
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}🚀 BrainCargo Comprehensive Test Runner{Colors.END}")
    print(f"{Colors.BOLD}Testing the refactored pipeline architecture{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    if args.cleanup:
        success = cleanup_environment()
        sys.exit(0 if success else 1)
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please fix issues before running tests.")
        sys.exit(1)
    
    test_results = {}
    
    try:
        if args.quick:
            # Quick test - only pipeline architecture
            print_info("Running quick test (pipeline architecture only)")
            test_results['pipeline'] = test_pipeline_architecture()
            
        elif args.service_only:
            # Service integration tests only
            print_info("Running service integration tests only")
            test_results['service'] = test_service_integration()
            
        else:
            # Complete test suite
            print_info("Running complete test suite")
            
            # Test pipeline architecture first (faster, catches basic issues)
            test_results['pipeline'] = test_pipeline_architecture()
            
            # If pipeline tests pass, run service integration
            if test_results['pipeline']:
                test_results['service'] = test_service_integration()
                
                # If service tests pass, run complete workflow
                if test_results['service']:
                    test_results['workflow'] = test_complete_workflow()
            else:
                print_warning("Skipping service tests due to pipeline test failures")
    
    except KeyboardInterrupt:
        print_warning("Tests interrupted by user")
        if not args.no_cleanup:
            cleanup_environment()
        sys.exit(1)
    
    # Print results summary
    print_header("Test Results Summary")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        if result:
            print_success(f"{test_name.title()} Tests")
            passed_tests += 1
        else:
            print_error(f"{test_name.title()} Tests")
    
    print(f"\n{Colors.BOLD}Overall Results: {passed_tests}/{total_tests} test suites passed{Colors.END}")
    
    # Cleanup unless explicitly disabled
    if not args.no_cleanup:
        print_info("Cleaning up test environment...")
        cleanup_environment()
    
    # Determine overall success
    if passed_tests == total_tests and total_tests > 0:
        print_success("🎉 All tests passed! The refactored pipeline is working correctly.")
        print_info("✅ Ready for deployment!")
        success = True
    elif passed_tests >= total_tests * 0.8 and total_tests > 0:
        print_warning(f"⚠️ Most tests passed ({passed_tests}/{total_tests}). Minor issues detected.")
        print_info("🔍 Review failures and consider fixing before deployment.")
        success = True
    else:
        print_error(f"❌ Tests failed ({total_tests - passed_tests}/{total_tests}). Architecture needs attention.")
        print_info("🛠️ Fix issues before deployment.")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
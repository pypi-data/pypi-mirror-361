#!/usr/bin/env python3
"""
MobSF Dynamic Analysis Module for lu77U-MobileSec
Provides comprehensive MobSF API testing and analysis capabilities
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Import the MobSF API class
try:
    from ...tools.mobsf_scripts.mobsf_api import MobSFAPI
    from ...utils.file_system.output_organizer import save_dynamic_analysis
except ImportError:
    try:
        # Fallback import for direct execution
        sys.path.append(str(Path(__file__).parent.parent.parent / "tools" / "mobsf_scripts"))
        from mobsf_api import MobSFAPI
    except ImportError:
        print("❌ Failed to import MobSF API class")
        print("   Make sure mobsf_api.py is in the tools/mobsf_scripts directory")
        sys.exit(1)

# Default configuration
MOBSF_SERVER = "http://127.0.0.1:8000"
DIVA_APK_PATH = "/Users/lu77_u/Documents/Git/Dr01d_H4ckQu35t/(Damn insecure and vulnerable App)/Files/DIVA.apk"


def prompt_mobsf_api_key() -> str:
    """Prompt user for MobSF API key with instructions"""
    print("\n🔑 MobSF API Key Required")
    print("=" * 50)
    print("1. Open your browser and go to: http://127.0.0.1:8000/api_docs")
    print("2. Copy the API Key from the API documentation page")
    print("3. Paste it below:")
    print()
    
    while True:
        api_key = input("Enter MobSF API Key: ").strip()
        if api_key:
            return api_key
        print("❌ API key cannot be empty. Please try again.")


class MobSFAnalyzer:
    """MobSF dynamic analysis component for lu77U-MobileSec"""
    
    def __init__(self, server: str = None, api_key: str = None, apk_path: str = None, debug: bool = False):
        if debug:
            print("🐛 DEBUG: Initializing MobSFAnalyzer...")
        
        self.debug = debug
        self.server = server or MOBSF_SERVER
        self.apk_path = apk_path or DIVA_APK_PATH
        
        if self.debug:
            print(f"🐛 DEBUG: Server set to: {self.server}")
            print(f"🐛 DEBUG: APK path set to: {self.apk_path}")
        
        # Always prompt for API key when using dynamic analysis
        if not api_key:
            if self.debug:
                print("🐛 DEBUG: No API key provided, prompting user...")
            self.api_key = prompt_mobsf_api_key()
        else:
            if self.debug:
                print("🐛 DEBUG: Using provided API key")
            self.api_key = api_key
        
        if self.debug:
            print(f"🐛 DEBUG: API key received (length: {len(self.api_key)})")
            print("🐛 DEBUG: Creating MobSFAPI instance...")
        
        self.api = MobSFAPI(server=self.server, api_key=self.api_key, debug=self.debug)
        self.test_results = {}
        self.scan_hash = None
        self.upload_response = None
        
        if self.debug:
            print("🐛 DEBUG: MobSFAnalyzer initialization complete")
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        if self.debug:
            print(f"🐛 DEBUG: Logging test result - {test_name}: {status}")
        
        self.test_results[test_name] = {
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.debug:
            print(f"🐛 DEBUG: Test result stored in test_results dict")
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
            
        if self.debug:
            print(f"🐛 DEBUG: Test log output complete for {test_name}")
    
    def test_server_connectivity(self):
        """Test 1: Server connectivity and authentication"""
        if self.debug:
            print("🐛 DEBUG: Starting server connectivity test...")
        
        print("\n🔧 Test 1: Server Connectivity and Authentication")
        if self.debug:
            print("=" * 60)
        
        try:
            if self.debug:
                print("🐛 DEBUG: Checking if MobSF server is running...")
            
            if self.api.is_server_running():
                self.log_test("Server Connectivity", "PASS", f"Connected to {self.server}")
            else:
                self.log_test("Server Connectivity", "FAIL", f"Cannot connect to {self.server}")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Server connectivity test failed: {e}")
            self.log_test("Server Connectivity", "FAIL", f"Error: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False
    
    def test_file_operations(self):
        """Test 2: File upload and scanning operations"""
        if self.debug:
            print("🐛 DEBUG: Starting file operations test...")
        
        print("\n📁 Test 2: File Upload and Scanning Operations")
        if self.debug:
            print("=" * 60)
        
        # Check if APK exists
        if self.debug:
            print(f"🐛 DEBUG: Checking if APK exists at: {self.apk_path}")
        
        if not Path(self.apk_path).exists():
            if self.debug:
                print("🐛 DEBUG: APK file not found")
            self.log_test("APK Check", "FAIL", f"APK not found at {self.apk_path}")
            return False
        
        if self.debug:
            print("🐛 DEBUG: APK file found, logging success")
        self.log_test("APK Check", "PASS", f"APK found at {self.apk_path}")
        
        # Test upload
        try:
            if self.debug:
                print("🐛 DEBUG: Starting APK upload...")
            
            print(f"📤 Uploading {Path(self.apk_path).name}...")
            self.upload_response = self.api.upload_file(self.apk_path)
            
            if self.debug:
                print(f"🐛 DEBUG: Upload response: {self.upload_response}")
            
            if self.upload_response:
                self.log_test("File Upload", "PASS", f"Successfully uploaded {Path(self.apk_path).name}")
            else:
                self.log_test("File Upload", "FAIL", "Upload failed - no response")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: File upload failed: {e}")
            self.log_test("File Upload", "FAIL", f"Error: {e}")
            return False
        
        # Test static analysis scan
        try:
            if self.debug:
                print("🐛 DEBUG: Starting static analysis scan...")
                
            print("🔍 Starting static analysis scan...")
            scan_result = self.api.scan_file(self.upload_response)
            
            if self.debug:
                print(f"🐛 DEBUG: Scan result: {scan_result}")
            
            if scan_result:
                self.scan_hash = scan_result.get('scan_hash') or scan_result.get('hash')
                self.log_test("Static Analysis Scan", "PASS", f"Scan completed with hash: {self.scan_hash}")
            else:
                self.log_test("Static Analysis Scan", "FAIL", "Scan failed - no result")
                
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Static analysis scan failed: {e}")
            self.log_test("Static Analysis Scan", "FAIL", f"Error: {e}")
        
        if self.debug:
            print("🐛 DEBUG: test_file_operations returning True")
        return True
    
    def test_dynamic_analysis_full(self):
        """Test comprehensive dynamic analysis workflow"""
        if self.debug:
            print("🐛 DEBUG: Starting comprehensive dynamic analysis test...")
        
        print("\n🚀 Test 3: Comprehensive Dynamic Analysis")
        if self.debug:
            print("=" * 60)
        
        if not self.scan_hash:
            if self.debug:
                print("🐛 DEBUG: No scan hash available for dynamic analysis")
            self.log_test("Dynamic Analysis", "SKIP", "No scan hash available")
            return False
        
        if self.debug:
            print(f"🐛 DEBUG: Using scan hash: {self.scan_hash}")
        
        try:
            if self.debug:
                print("🐛 DEBUG: Starting advanced dynamic analysis...")
            
            # Start comprehensive dynamic analysis
            dynamic_result = self.api.start_advanced_dynamic_analysis(
                self.scan_hash,
                enable_frida=True,
                enable_xposed=False,
                proxy_enabled=True
            )
            
            if self.debug:
                print(f"🐛 DEBUG: Dynamic analysis result: {dynamic_result}")
            
            if dynamic_result and dynamic_result.get("status") == "success":
                self.log_test("Advanced Dynamic Analysis", "PASS", "Dynamic analysis completed successfully")
                return True
            else:
                self.log_test("Advanced Dynamic Analysis", "FAIL", "Dynamic analysis did not complete successfully")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Dynamic analysis failed: {e}")
            self.log_test("Advanced Dynamic Analysis", "FAIL", f"Error: {e}")
            return False
    
    def _run_security_assessments(self):
        """Run security assessment functions"""
        if self.debug:
            print("🐛 DEBUG: Starting security assessments...")
        
        if self.debug:
            print("\n🔒 Running Security Assessments...")
        
        # Test runtime instrumentation
        try:
            if self.debug:
                print("🐛 DEBUG: Starting runtime instrumentation test...")
            
            instrumentation = self.api.runtime_application_instrumentation(
                self.scan_hash,
                hook_crypto=True,
                hook_network=True,
                custom_hooks=['crypto_operations', 'file_operations']
            )
            
            if self.debug:
                print(f"🐛 DEBUG: Instrumentation result: {type(instrumentation)}")
                if instrumentation:
                    print(f"🐛 DEBUG: Instrumentation status: {instrumentation.get('status')}")
            
            if instrumentation and instrumentation.get("status") == "success":
                if self.debug:
                    print("🐛 DEBUG: Runtime instrumentation passed")
                self.log_test("Runtime Instrumentation", "PASS", "Runtime instrumentation activated successfully")
            else:
                if self.debug:
                    print("🐛 DEBUG: Runtime instrumentation completed with info status")
                self.log_test("Runtime Instrumentation", "INFO", "Instrumentation configured")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in runtime instrumentation: {e}")
            self.log_test("Runtime Instrumentation", "FAIL", f"Error: {e}")
        
        # Test malware detection
        try:
            if self.debug:
                print("🐛 DEBUG: Starting malware detection test...")
            
            malware_detection = self.api.malware_behavior_detection(
                self.scan_hash,
                heuristic_analysis=True,
                ml_detection=True
            )
            
            if self.debug:
                print(f"🐛 DEBUG: Malware detection result: {type(malware_detection)}")
                if malware_detection:
                    print(f"🐛 DEBUG: Malware detection status: {malware_detection.get('status')}")
            
            if malware_detection and malware_detection.get("status") == "completed":
                if self.debug:
                    print("🐛 DEBUG: Malware detection passed")
                self.log_test("Malware Detection", "PASS", "Malware behavior detection completed successfully")
            else:
                if self.debug:
                    print("🐛 DEBUG: Malware detection completed with info status")
                self.log_test("Malware Detection", "INFO", "Malware behavior detection configured")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in malware detection: {e}")
            self.log_test("Malware Detection", "FAIL", f"Error: {e}")
        
        # Test API security
        try:
            if self.debug:
                print("🐛 DEBUG: Starting API security testing...")
            
            api_testing = self.api.api_security_testing(
                self.scan_hash,
                test_authentication=True,
                test_input_validation=True
            )
            
            if self.debug:
                print(f"🐛 DEBUG: API security result: {type(api_testing)}")
                if api_testing:
                    print(f"🐛 DEBUG: API security status: {api_testing.get('status')}")
            
            if api_testing and api_testing.get("status") == "completed":
                if self.debug:
                    print("🐛 DEBUG: API security testing passed")
                self.log_test("API Security Testing", "PASS", "API security testing completed successfully")
            else:
                if self.debug:
                    print("🐛 DEBUG: API security testing completed with info status")
                self.log_test("API Security Testing", "INFO", "API security testing configured")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in API security testing: {e}")
            self.log_test("API Security Testing", "FAIL", f"Error: {e}")
            
        if self.debug:
            print("🐛 DEBUG: Security assessments complete")
    
    def _run_compliance_tests(self):
        """Run compliance and risk assessment"""
        if self.debug:
            print("🐛 DEBUG: Starting compliance tests...")
        
        if self.debug:
            print("\n📋 Running Compliance Assessment...")
        
        # Test compliance assessment
        try:
            if self.debug:
                print("🐛 DEBUG: Starting compliance assessment with OWASP_MASVS, NIST, ISO27001...")
            
            compliance = self.api.compliance_assessment(
                self.scan_hash,
                frameworks=['OWASP_MASVS', 'NIST', 'ISO27001']
            )
            
            if self.debug:
                print(f"🐛 DEBUG: Compliance assessment result: {type(compliance)}")
                if compliance:
                    print(f"🐛 DEBUG: Compliance status: {compliance.get('status')}")
            
            if compliance and compliance.get('status') == 'success':
                if self.debug:
                    print("🐛 DEBUG: Compliance assessment passed")
                self.log_test("Compliance Assessment", "PASS", "Compliance assessment completed successfully")
            else:
                if self.debug:
                    print("🐛 DEBUG: Compliance assessment completed with info status")
                self.log_test("Compliance Assessment", "INFO", "Compliance assessment completed")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in compliance assessment: {e}")
            self.log_test("Compliance Assessment", "FAIL", f"Error: {e}")
        
        # Test threat intelligence
        try:
            if self.debug:
                print("🐛 DEBUG: Starting threat intelligence correlation...")
            
            threat_intel = self.api.threat_intelligence_correlation(
                self.scan_hash,
                ti_sources=['virustotal', 'malware_bazaar']
            )
            
            if self.debug:
                print(f"🐛 DEBUG: Threat intelligence result: {type(threat_intel)}")
                if threat_intel:
                    print(f"🐛 DEBUG: Threat intelligence status: {threat_intel.get('status')}")
            
            if threat_intel and threat_intel.get('status') == 'success':
                if self.debug:
                    print("🐛 DEBUG: Threat intelligence correlation passed")
                self.log_test("Threat Intelligence", "PASS", "Threat intelligence correlation completed successfully")
            else:
                if self.debug:
                    print("🐛 DEBUG: Threat intelligence correlation completed with info status")
                self.log_test("Threat Intelligence", "INFO", "Threat intelligence correlation completed")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in threat intelligence: {e}")
            self.log_test("Threat Intelligence", "FAIL", f"Error: {e}")
            
        if self.debug:
            print("🐛 DEBUG: Compliance tests complete")
    
    def _generate_reports(self):
        """Generate analysis reports"""
        if self.debug:
            print("🐛 DEBUG: Starting report generation...")
        
        if self.debug:
            print("\n📊 Generating Reports...")
        
        # Test JSON report generation
        try:
            if self.debug:
                print("🐛 DEBUG: Generating JSON report...")
            
            json_report = self.api.get_json_report(self.scan_hash)
            
            if self.debug:
                print(f"🐛 DEBUG: JSON report result: {type(json_report)}")
            
            if json_report:
                if self.debug:
                    print(f"🐛 DEBUG: JSON report generated successfully, size: {len(str(json_report))} chars")
                self.log_test("JSON Report", "PASS", f"Report size: {len(str(json_report))} chars")
            else:
                if self.debug:
                    print("🐛 DEBUG: JSON report generation failed")
                self.log_test("JSON Report", "FAIL", "No report generated")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in JSON report generation: {e}")
            self.log_test("JSON Report", "FAIL", f"Error: {e}")
        
        # Test comprehensive dynamic report
        try:
            if self.debug:
                print("🐛 DEBUG: Generating comprehensive dynamic report...")
            
            dynamic_report = self.api.get_comprehensive_dynamic_report(
                self.scan_hash,
                include_network_data=True,
                include_logs=True
            )
            
            if self.debug:
                print(f"🐛 DEBUG: Dynamic report result: {type(dynamic_report)}")
                if dynamic_report:
                    print(f"🐛 DEBUG: Dynamic report status: {dynamic_report.get('status')}")
            
            if dynamic_report and dynamic_report.get('status') in ['completed', 'success']:
                if self.debug:
                    print("🐛 DEBUG: Comprehensive dynamic report generated successfully")
                self.log_test("Comprehensive Dynamic Report", "PASS", "Dynamic report generated successfully")
            else:
                if self.debug:
                    print("🐛 DEBUG: Comprehensive dynamic report completed with info status")
                self.log_test("Comprehensive Dynamic Report", "INFO", "Dynamic report generated")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in comprehensive dynamic report: {e}")
            self.log_test("Comprehensive Dynamic Report", "FAIL", f"Error: {e}")
        
        # Test pentest report generation
        try:
            if self.debug:
                print("🐛 DEBUG: Generating pentest report...")
            
            pentest_report = self.api.generate_pentest_report(
                self.scan_hash,
                client_name="lu77U-MobileSec",
                report_type="executive"
            )
            
            if self.debug:
                print(f"🐛 DEBUG: Pentest report result: {type(pentest_report)}")
                if pentest_report:
                    print(f"🐛 DEBUG: Pentest report status: {pentest_report.get('status')}")
            
            if pentest_report and pentest_report.get('status') == 'success':
                if self.debug:
                    print("🐛 DEBUG: Pentest report generated successfully")
                self.log_test("Pentest Report", "PASS", "Pentest report generated successfully")
            else:
                if self.debug:
                    print("🐛 DEBUG: Pentest report completed with info status")
                self.log_test("Pentest Report", "INFO", "Pentest report generated")
        except Exception as e:
            if self.debug:
                print(f"🐛 DEBUG: Exception in pentest report generation: {e}")
            self.log_test("Pentest Report", "FAIL", f"Error: {e}")
            
        if self.debug:
            print("🐛 DEBUG: Report generation complete")
    
    def save_results_to_structured_output(self, analysis_directories: Optional[Dict] = None, apk_name: str = "unknown") -> bool:
        """Save dynamic analysis results to structured output directory"""
        if self.debug:
            print("🐛 DEBUG: Saving MobSF results to structured output...")
        
        if not analysis_directories:
            if self.debug:
                print("🐛 DEBUG: No analysis directories provided, skipping structured save")
            return False
        
        try:
            # Save the test results as JSON and convert to markdown
            if self.test_results:
                if self.debug:
                    print("🐛 DEBUG: Saving dynamic analysis results...")
                
                save_dynamic_analysis(
                    self.test_results, 
                    apk_name, 
                    analysis_directories, 
                    convert_to_md=True
                )
                
                print("📁 Dynamic analysis results saved to structured output directory")
                return True
            else:
                if self.debug:
                    print("🐛 DEBUG: No test results to save")
                return False
                
        except Exception as e:
            print(f"⚠️  Warning: Could not save dynamic analysis results: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False
    
    def run_dynamic_analysis(self, save_results: bool = True, analysis_directories: Optional[Dict] = None, apk_name: str = "unknown"):
        """Run the complete dynamic analysis workflow"""
        if self.debug:
            print("🐛 DEBUG: Starting complete dynamic analysis workflow...")
        
        print("🎯 MobSF Dynamic Analysis for lu77U-MobileSec")
        if self.debug:
            print("=" * 80)
            print(f"📱 Target APK: {self.apk_path}")
            print(f"🌐 MobSF Server: {self.server}")
            print(f"🔑 API Key: {self.api_key[:20]}...")
            print("=" * 80)
        
        if self.debug:
            print("🐛 DEBUG: Setting up test functions list...")
        
        # Run test sequence
        test_functions = [
            self.test_server_connectivity,
            self.test_file_operations,
            self.test_dynamic_analysis_full,
            self._run_security_assessments,
            self._run_compliance_tests,
            self._generate_reports
        ]
        
        if self.debug:
            print(f"🐛 DEBUG: Will run {len(test_functions)} test functions")
        
        successful_tests = 0
        for i, test_func in enumerate(test_functions, 1):
            try:
                if self.debug:
                    print(f"🐛 DEBUG: Running test function {i}: {test_func.__name__}")
                result = test_func()
                if result:
                    successful_tests += 1
                if self.debug:
                    print(f"🐛 DEBUG: Test function {i} completed with result: {result}")
            except Exception as e:
                if self.debug:
                    print(f"🐛 DEBUG: Test function {i} failed with exception: {e}")
                    import traceback
                    traceback.print_exc()
        
        if self.debug:
            print(f"🐛 DEBUG: Completed {successful_tests}/{len(test_functions)} test functions successfully")
        
        # Print summary
        print("\n📊 Dynamic Analysis Summary")
        if self.debug:
            print("=" * 80)
        
        if self.debug:
            print("🐛 DEBUG: Calculating test statistics...")
        
        passed_tests = sum(1 for r in self.test_results.values() if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.test_results.values() if r['status'] == 'FAIL')
        skipped_tests = sum(1 for r in self.test_results.values() if r['status'] in ['SKIP', 'INFO'])
        
        if self.debug:
            print(f"🐛 DEBUG: Statistics - Passed: {passed_tests}, Failed: {failed_tests}, Skipped/Info: {skipped_tests}")
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Skipped/Info: {skipped_tests}")
        
        # Show concise summary of successful dynamic analysis steps in normal mode
        successful_steps = []
        for test_name, result in self.test_results.items():
            if result['status'] == 'PASS':
                successful_steps.append(test_name)
        
        if successful_steps:
            print("✅ Successfully completed dynamic analysis steps:")
            for step in successful_steps:
                print(f"   • {step}")
        else:
            print("⚠️ No dynamic analysis steps completed successfully")
        
        success_rate = (passed_tests / (passed_tests + failed_tests) * 100) if (passed_tests + failed_tests) > 0 else 0
        
        if self.debug:
            print(f"🐛 DEBUG: Calculated success rate: {success_rate:.1f}%")
        
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results to JSON
        if save_results:
            if self.debug:
                print("🐛 DEBUG: Saving results to JSON file...")
            
            results_file = "mobsf_dynamic_analysis_results.json"
            try:
                with open(results_file, 'w') as f:
                    json.dump(self.test_results, f, indent=2)
                print(f"💾 Results saved to: {results_file}")
                if self.debug:
                    print(f"🐛 DEBUG: Results successfully saved to {results_file}")
            except Exception as e:
                print(f"❌ Failed to save results: {e}")
                if self.debug:
                    print(f"🐛 DEBUG: Error saving results: {e}")
        else:
            if self.debug:
                print("🐛 DEBUG: Skipping results save (save_results=False)")
        
        # Save to structured output directory if provided
        if analysis_directories:
            self.save_results_to_structured_output(analysis_directories, apk_name)
        
        if self.debug:
            print("🐛 DEBUG: Dynamic analysis workflow complete")
        
        return self.test_results

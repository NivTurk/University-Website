#!/usr/bin/env python3
"""
Flask API Tester - Updated for Current Project Version

This script tests your Flask API endpoints with the actual data structure
and response formats used in your current implementation.

Usage:
    python3 api_tester.py

Output:
    - Creates api_test_results.txt with detailed results
    - Shows progress in terminal
"""

import requests
import json
import time
import datetime
import sys
import traceback

# Configuration
VERSION = "2.0.0"
BASE_URL = "http://localhost:5000/api/courses"
HEADERS = {'Content-Type': 'application/json'}
NUM_ITERATIONS = 10
DELAY_BETWEEN_ITERATIONS = 2

class APITester:
    def __init__(self, output_file="api_test_results.txt"):
        self.output_file = output_file
        self.results = []
        self.iteration_count = 0
        self.start_time = None
        
    def log(self, message, level="INFO"):
        """Log message to both console and results"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.results.append(log_entry)
    
    def log_separator(self, title=""):
        """Add a separator line"""
        separator = "=" * 80
        if title:
            separator = f"=== {title} " + "=" * (80 - len(title) - 5)
        self.log(separator)
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=None, description=""):
        """Test a single endpoint and return detailed results"""
        url = f"{BASE_URL}{endpoint}" if endpoint else BASE_URL
        
        test_result = {
            'method': method,
            'url': url,
            'description': description,
            'timestamp': datetime.datetime.now().isoformat(),
            'success': False,
            'status_code': None,
            'response_time_ms': None,
            'response_text': '',
            'error': None
        }
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=HEADERS, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=HEADERS, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)
            
            test_result['status_code'] = response.status_code
            test_result['response_time_ms'] = response_time
            test_result['response_text'] = response.text[:500] + ('...' if len(response.text) > 500 else '')
            
            if expected_status:
                test_result['success'] = response.status_code == expected_status
            else:
                test_result['success'] = 200 <= response.status_code < 300
            
            status_icon = "✅" if test_result['success'] else "❌"
            self.log(f"{status_icon} {description}: {response.status_code} ({response_time}ms)")
            
            return test_result, response
            
        except Exception as e:
            test_result['error'] = str(e)
            test_result['response_time_ms'] = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
            self.log(f"❌ {description}: ERROR - {str(e)}", "ERROR")
            return test_result, None
    
    def run_single_iteration(self):
        """Run one complete test iteration"""
        self.iteration_count += 1
        iteration_results = {
            'iteration': self.iteration_count,
            'start_time': datetime.datetime.now().isoformat(),
            'tests': [],
            'created_course_id': None,
            'summary': {'total': 0, 'passed': 0, 'failed': 0}
        }
        
        self.log_separator(f"ITERATION {self.iteration_count}")
        
        # Test 1: Get all courses (initial state)
        result, response = self.test_endpoint('GET', '', expected_status=200, description="Get all courses (initial)")
        iteration_results['tests'].append(result)
        
        initial_courses = []
        if response and response.status_code == 200:
            try:
                initial_courses = response.json()
                self.log(f"Initial courses count: {len(initial_courses)}")
            except:
                self.log("Failed to parse initial courses JSON", "WARNING")
        
        # Test 2: Create a new course (using correct field name 'syllabus')
        course_data = {
            "name": f"Test Course {self.iteration_count}",
            "syllabus": f"Test syllabus for iteration {self.iteration_count} created at {datetime.datetime.now()}"
        }
        
        result, response = self.test_endpoint('POST', '', data=course_data, expected_status=201, description="Create course")
        iteration_results['tests'].append(result)
        
        # Extract course ID if creation was successful
        if response and response.status_code == 201:
            try:
                course_json = response.json()
                iteration_results['created_course_id'] = course_json.get('_id')
                self.log(f"Created course ID: {iteration_results['created_course_id']}")
            except:
                self.log("Failed to parse created course JSON", "WARNING")
        
        # Test 3: Get all courses (after creation)
        result, response = self.test_endpoint('GET', '', expected_status=200, description="Get all courses (after create)")
        iteration_results['tests'].append(result)
        
        if response and response.status_code == 200:
            try:
                after_courses = response.json()
                self.log(f"Courses count after creation: {len(after_courses)}")
                if len(after_courses) != len(initial_courses) + 1:
                    self.log(f"WARNING: Expected {len(initial_courses) + 1} courses, found {len(after_courses)}", "WARNING")
            except:
                self.log("Failed to parse courses JSON after creation", "WARNING")
        
        # Test 4: Get single course (if we have an ID)
        if iteration_results['created_course_id']:
            result, response = self.test_endpoint('GET', f"/{iteration_results['created_course_id']}", expected_status=200, description="Get single course")
            iteration_results['tests'].append(result)
        
        # Test 5: Update course (if we have an ID)
        if iteration_results['created_course_id']:
            update_data = {
                "name": f"Updated Course {self.iteration_count}",
                "syllabus": f"Updated syllabus for iteration {self.iteration_count}"
            }
            result, response = self.test_endpoint('PUT', f"/{iteration_results['created_course_id']}", data=update_data, expected_status=200, description="Update course")
            iteration_results['tests'].append(result)
        
        # Test 6: Delete course (if we have an ID)
        if iteration_results['created_course_id']:
            result, response = self.test_endpoint('DELETE', f"/{iteration_results['created_course_id']}", expected_status=200, description="Delete course")
            iteration_results['tests'].append(result)
        
        # Test 7: Get all courses (after deletion)
        result, response = self.test_endpoint('GET', '', expected_status=200, description="Get all courses (after delete)")
        iteration_results['tests'].append(result)
        
        if response and response.status_code == 200:
            try:
                final_courses = response.json()
                self.log(f"Final courses count: {len(final_courses)}")
                if len(final_courses) != len(initial_courses):
                    self.log(f"WARNING: Expected {len(initial_courses)} courses at end, found {len(final_courses)}", "WARNING")
            except:
                self.log("Failed to parse final courses JSON", "WARNING")
        
        # Test 8: Test invalid ID error handling
        result, response = self.test_endpoint('GET', '/invalid_id', expected_status=400, description="Test invalid ID handling")
        iteration_results['tests'].append(result)
        
        # Test 9: Test validation errors
        invalid_data = {"name": "AB"}  # Too short, missing syllabus
        result, response = self.test_endpoint('POST', '', data=invalid_data, expected_status=400, description="Test validation errors")
        iteration_results['tests'].append(result)
        
        # Test 10: Test duplicate name handling
        if len(initial_courses) > 0:
            # Try to create a course with the same name as an existing one
            duplicate_data = {
                "name": initial_courses[0]['name'] if initial_courses else "Test Course 1",
                "syllabus": "This should fail due to duplicate name"
            }
            result, response = self.test_endpoint('POST', '', data=duplicate_data, expected_status=409, description="Test duplicate name handling")
            iteration_results['tests'].append(result)
        else:
            # Create a course and then try to create another with the same name
            temp_course_data = {
                "name": "Duplicate Test Course",
                "syllabus": "First course for duplicate test"
            }
            result, response = self.test_endpoint('POST', '', data=temp_course_data, expected_status=201, description="Create course for duplicate test")
            iteration_results['tests'].append(result)
            
            # Now try to create a duplicate
            result, response = self.test_endpoint('POST', '', data=temp_course_data, expected_status=409, description="Test duplicate name handling")
            iteration_results['tests'].append(result)
            
            # Clean up the test course
            if response and len(iteration_results['tests']) >= 2:
                prev_response = None
                for test in iteration_results['tests']:
                    if test['description'] == "Create course for duplicate test" and test['success']:
                        # Extract ID from previous successful creation
                        try:
                            # We need to get the ID from the actual response, but we don't store it
                            # Let's just try to find and delete by name
                            cleanup_result, cleanup_response = self.test_endpoint('GET', '', expected_status=200, description="Get courses for cleanup")
                            if cleanup_response and cleanup_response.status_code == 200:
                                courses = cleanup_response.json()
                                for course in courses:
                                    if course['name'] == "Duplicate Test Course":
                                        self.test_endpoint('DELETE', f"/{course['_id']}", expected_status=200, description="Cleanup duplicate test course")
                                        break
                        except:
                            self.log("Failed to cleanup duplicate test course", "WARNING")
        
        # Calculate summary
        iteration_results['summary']['total'] = len(iteration_results['tests'])
        iteration_results['summary']['passed'] = sum(1 for test in iteration_results['tests'] if test['success'])
        iteration_results['summary']['failed'] = iteration_results['summary']['total'] - iteration_results['summary']['passed']
        
        iteration_results['end_time'] = datetime.datetime.now().isoformat()
        
        # Log iteration summary
        summary = iteration_results['summary']
        self.log(f"Iteration {self.iteration_count} Summary: {summary['passed']}/{summary['total']} passed, {summary['failed']} failed")
        
        return iteration_results
    
    def run_batch_tests(self):
        """Run multiple test iterations"""
        self.start_time = datetime.datetime.now()
        
        # Header
        self.log_separator("FLASK API BATCH TESTER STARTED")
        self.log(f"Tester Version: {VERSION}")
        self.log(f"Start time: {self.start_time}")
        self.log(f"Number of iterations: {NUM_ITERATIONS}")
        self.log(f"Target URL: {BASE_URL}")
        self.log(f"Delay between iterations: {DELAY_BETWEEN_ITERATIONS} seconds")
        
        # Test server connection first
        self.log_separator("INITIAL CONNECTION TEST")
        try:
            response = requests.get(BASE_URL, timeout=5)
            self.log(f"✅ Server connection successful: {response.status_code}")
        except Exception as e:
            self.log(f"❌ Server connection failed: {e}", "ERROR")
            self.log("Aborting tests - Flask server appears to be down", "ERROR")
            return
        
        # Run iterations
        all_iterations = []
        
        for i in range(NUM_ITERATIONS):
            try:
                iteration_result = self.run_single_iteration()
                all_iterations.append(iteration_result)
                
                # Wait between iterations (except for the last one)
                if i < NUM_ITERATIONS - 1:
                    self.log(f"Waiting {DELAY_BETWEEN_ITERATIONS} seconds before next iteration...")
                    time.sleep(DELAY_BETWEEN_ITERATIONS)
                    
            except KeyboardInterrupt:
                self.log("Tests interrupted by user", "WARNING")
                break
            except Exception as e:
                self.log(f"Iteration {i+1} failed with error: {e}", "ERROR")
                self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
        
        # Final summary
        self.log_separator("BATCH TEST SUMMARY")
        
        end_time = datetime.datetime.now()
        total_duration = end_time - self.start_time
        
        self.log(f"End time: {end_time}")
        self.log(f"Total duration: {total_duration}")
        self.log(f"Completed iterations: {len(all_iterations)}")
        
        # Aggregate statistics
        total_tests = sum(it['summary']['total'] for it in all_iterations)
        total_passed = sum(it['summary']['passed'] for it in all_iterations)
        total_failed = sum(it['summary']['failed'] for it in all_iterations)
        
        self.log(f"Total tests run: {total_tests}")
        self.log(f"Total passed: {total_passed}")
        self.log(f"Total failed: {total_failed}")
        self.log(f"Overall success rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Analyze consistency
        self.log_separator("CONSISTENCY ANALYSIS")
        
        if len(all_iterations) > 1:
            pass_counts = [it['summary']['passed'] for it in all_iterations]
            if len(set(pass_counts)) == 1:
                self.log("✅ All iterations had consistent results")
            else:
                self.log("❌ Inconsistent results detected!")
                self.log(f"Pass counts per iteration: {pass_counts}")
                
                # Analyze which tests are failing inconsistently
                test_descriptions = set()
                for iteration in all_iterations:
                    for test in iteration['tests']:
                        test_descriptions.add(test['description'])
                
                for desc in test_descriptions:
                    results = []
                    for iteration in all_iterations:
                        for test in iteration['tests']:
                            if test['description'] == desc:
                                results.append(test['success'])
                                break
                    
                    if len(set(results)) > 1:
                        self.log(f"❌ Inconsistent test: {desc}")
                        self.log(f"   Results: {results}")
        
        # Save detailed results to file
        self.save_results_to_file(all_iterations)
    
    def save_results_to_file(self, all_iterations):
        """Save detailed results to file"""
        try:
            with open(self.output_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("FLASK API BATCH TEST RESULTS\n")
                f.write("="*80 + "\n\n")
                
                f.write("SUMMARY:\n")
                f.write("-"*40 + "\n")
                for line in self.results:
                    f.write(line + "\n")
                
                f.write("\n\n" + "="*80 + "\n")
                f.write("DETAILED ITERATION DATA (JSON):\n")
                f.write("="*80 + "\n\n")
                
                f.write(json.dumps(all_iterations, indent=2))
                
            self.log(f"✅ Detailed results saved to: {self.output_file}")
            
        except Exception as e:
            self.log(f"❌ Failed to save results to file: {e}", "ERROR")

def main():
    print(f"🔄 Flask API Tester v{VERSION} - Updated Version")
    print("This tester matches your current Flask API implementation")
    print(f"Running {NUM_ITERATIONS} iterations with {DELAY_BETWEEN_ITERATIONS}s delays...")
    print()
    
    # Check dependencies
    try:
        import requests
    except ImportError:
        print("❌ Missing 'requests' library. Install with: pip install requests")
        sys.exit(1)
    
    # Run tests
    tester = APITester()
    tester.run_batch_tests()
    
    print(f"\n🏁 Testing complete! (Tester v{VERSION})")
    print(f"📄 Results saved to: {tester.output_file}")

if __name__ == "__main__":
    main()
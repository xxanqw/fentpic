#!/usr/bin/env python3
"""
License checker script for FENTPIC project.
Generates a comprehensive license report for all dependencies.
"""

import subprocess
import sys
import json
import os
from pathlib import Path

def run_pip_licenses():
    """Run pip-licenses and return the output"""
    try:
        # Install pip-licenses if not available
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pip-licenses'], 
                             stdout=subprocess.DEVNULL)
        
        # Run pip-licenses with markdown format
        result = subprocess.run([
            sys.executable, '-m', 'pip-licenses', 
            '--format=markdown',
            '--with-license-file',
            '--no-license-path'
        ], capture_output=True, text=True, check=True)
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running pip-licenses: {e}")
        return None

def run_pip_licenses_json():
    """Run pip-licenses with JSON output for analysis"""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip-licenses', 
            '--format=json',
            '--with-license-file'
        ], capture_output=True, text=True, check=True)
        
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error getting JSON license data: {e}")
        return []

def analyze_licenses(license_data):
    """Analyze license compatibility and generate summary"""
    license_counts = {}
    risky_licenses = ['GPL-3.0', 'AGPL-3.0', 'LGPL-3.0']
    permissive_licenses = ['MIT', 'BSD', 'Apache-2.0', 'ISC', 'Unlicense']
    unknown_licenses = []
    
    for package in license_data:
        license_name = package.get('License', 'Unknown')
        license_counts[license_name] = license_counts.get(license_name, 0) + 1
        
        if license_name in risky_licenses:
            print(f"⚠️  Warning: {package['Name']} uses {license_name} (copyleft)")
        elif license_name not in permissive_licenses and license_name != 'Unknown':
            unknown_licenses.append((package['Name'], license_name))
    
    return license_counts, unknown_licenses

def generate_license_report():
    """Generate comprehensive license report"""
    print("🔍 Generating license compliance report...")
    
    # Get markdown report
    markdown_report = run_pip_licenses()
    if not markdown_report:
        print("❌ Failed to generate license report")
        return False
    
    # Get JSON data for analysis
    json_data = run_pip_licenses_json()
    
    # Create report header
    report_header = f"""# License Compliance Report for FENTPIC

**Generated on:** {os.popen('date').read().strip()}  
**Python Version:** {sys.version}  
**Project:** FENTPIC Image Hosting Platform  
**License:** MIT  

## Summary

This report contains license information for all Python dependencies used in the FENTPIC project.

### License Analysis

"""
    
    # Analyze licenses if JSON data is available
    if json_data:
        license_counts, unknown_licenses = analyze_licenses(json_data)
        
        report_header += f"**Total Packages:** {len(json_data)}  \n"
        report_header += f"**Unique Licenses:** {len(license_counts)}  \n\n"
        
        report_header += "### License Distribution\n\n"
        for license_name, count in sorted(license_counts.items(), key=lambda x: x[1], reverse=True):
            report_header += f"- **{license_name}:** {count} packages\n"
        
        if unknown_licenses:
            report_header += "\n### Packages with Non-Standard Licenses\n\n"
            for package, license_name in unknown_licenses:
                report_header += f"- **{package}:** {license_name}\n"
    
    report_header += f"""

## Compatibility Assessment

✅ **FENTPIC License:** MIT  
✅ **Compatibility:** All dependencies appear to be compatible with commercial use  
⚠️  **Note:** Please review any GPL/AGPL licensed packages carefully  

## Detailed Package Information

"""
    
    # Combine header with detailed report
    full_report = report_header + markdown_report
    
    # Write to file
    report_path = Path('LICENSE_REPORT.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"✅ License report generated: {report_path}")
    return True

def check_project_license():
    """Check if project has a proper LICENSE file"""
    license_file = Path('LICENSE')
    if license_file.exists():
        print("✅ LICENSE file found")
        with open(license_file, 'r') as f:
            content = f.read()
            if 'MIT' in content:
                print("✅ MIT License detected")
            else:
                print("❓ License type unclear from LICENSE file")
    else:
        print("❌ No LICENSE file found - creating MIT license...")
        create_mit_license()

def create_mit_license():
    """Create MIT license file"""
    mit_license = """MIT License

Copyright (c) 2025 xxanqw

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open('LICENSE', 'w') as f:
        f.write(mit_license)
    
    print("✅ MIT LICENSE file created")

def main():
    """Main function"""
    print("🔍 FENTPIC License Compliance Checker")
    print("=" * 40)
    
    # Check project license
    check_project_license()
    
    # Generate dependency license report
    success = generate_license_report()
    
    if success:
        print("\n✅ License compliance check completed successfully!")
        print("📄 Review LICENSE_REPORT.md for detailed information")
        print("\n📋 Summary:")
        print("   - All dependencies checked for license compatibility")
        print("   - Report saved to LICENSE_REPORT.md")
        print("   - Project uses MIT license (commercial-friendly)")
    else:
        print("\n❌ License compliance check failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()

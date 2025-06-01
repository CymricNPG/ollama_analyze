"""
Copyright (C) 2025 Roland Spatzenegger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Reporting for Java code structure.
"""

import html
from typing import Dict, List
from java.models import JavaCodeData, JavaClass, JavaMethod, MethodReference


class JavaCodeHTMLGenerator:
    """Generates HTML documentation from JavaCodeData."""
    
    def __init__(self, java_code_data: JavaCodeData):
        self.data = java_code_data
        self.packages = self._organize_by_packages()
    
    def _organize_by_packages(self) -> Dict[str, List[JavaClass]]:
        """Organize classes by their packages."""
        packages = {}
        
        for java_class in self.data.classes:
            # Extract package from class name (assuming format like com.example.ClassName)
            class_parts = java_class.class_name.split('.')
            if len(class_parts) > 1:
                package_name = '.'.join(class_parts[:-1])
                class_name = class_parts[-1]
            else:
                package_name = "(default)"
                class_name = java_class.class_name
            
            if package_name not in packages:
                packages[package_name] = []
            
            packages[package_name].append(java_class)
        
        # Sort classes within each package
        for package in packages.values():
            package.sort(key=lambda cls: cls.class_name)
        
        return packages
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return html.escape(text) if text else ""
    
    def _generate_navigation(self) -> str:
        """Generate the navigation menu HTML."""
        nav_html = """
        <nav class="navigation">
            <h2>Classes by Package</h2>
            <div class="package-list">
        """
        
        # Sort packages alphabetically
        sorted_packages = sorted(self.packages.keys())
        
        for package_name in sorted_packages:
            classes = self.packages[package_name]
            nav_html += f"""
                <div class="package">
                    <h3 class="package-name">{self._escape_html(package_name)}</h3>
                    <ul class="class-list">
            """
            
            for java_class in classes:
                class_id = self._get_class_id(java_class.class_name)
                simple_name = java_class.class_name.split('.')[-1]
                nav_html += f"""
                        <li><a href="#{class_id}" class="class-link">{self._escape_html(simple_name)}</a></li>
                """
            
            nav_html += """
                    </ul>
                </div>
            """
        
        nav_html += """
            </div>
        </nav>
        """
        
        return nav_html
    
    def _get_class_id(self, class_name: str) -> str:
        """Generate a valid HTML ID for a class."""
        return f"class-{class_name.replace('.', '-')}"
    
    def _get_method_id(self, class_name: str, method_name: str) -> str:
        """Generate a valid HTML ID for a method."""
        return f"method-{class_name.replace('.', '-')}-{method_name}"
    
    def _generate_class_section(self, java_class: JavaClass) -> str:
        """Generate HTML section for a class."""
        class_id = self._get_class_id(java_class.class_name)
        simple_name = java_class.class_name.split('.')[-1]
        
        html_content = f"""
        <section class="class-section" id="{class_id}">
            <h2 class="class-title">{self._escape_html(simple_name)}</h2>
            <p class="full-class-name">Full name: {self._escape_html(java_class.class_name)}</p>
            
            <div class="class-content">
                <div class="javadoc-section">
                    <h3>Documentation</h3>
                    <div class="javadoc">
        """
        
        if java_class.java_doc:
            html_content += f"<pre>{self._escape_html(java_class.java_doc)}</pre>"
        else:
            html_content += "<p><em>No documentation available</em></p>"
        
        html_content += """
                    </div>
                </div>
                
                <div class="code-section">
                    <h3>Source Code</h3>
                    <pre class="code"><code>"""
        
        html_content += self._escape_html(java_class.code)
        
        html_content += """</code></pre>
                </div>
                
                <div class="methods-section">
                    <h3>Methods</h3>
        """
        
        # Get methods for this class
        class_methods = self.data.get_methods_by_class(java_class.class_name)
        
        if class_methods:
            html_content += "<ul class='method-list'>"
            for method in class_methods:
                method_id = self._get_method_id(method.src.class_name, method.src.method_name)
                html_content += f"""
                    <li><a href="#{method_id}" class="method-link">{self._escape_html(method.src.method_name)}</a></li>
                """
            html_content += "</ul>"
        else:
            html_content += "<p><em>No methods found</em></p>"
        
        html_content += """
                </div>
            </div>
        </section>
        """
        
        return html_content
    
    def _generate_method_section(self, method: JavaMethod) -> str:
        """Generate HTML section for a method."""
        method_id = self._get_method_id(method.src.class_name, method.src.method_name)
        
        html_content = f"""
        <section class="method-section" id="{method_id}">
            <h2 class="method-title">{self._escape_html(method.src.method_name)}</h2>
            <p class="method-class">Class: {self._escape_html(method.src.class_name)}</p>
            
            <div class="method-content">
                <div class="method-javadoc-section">
                    <h3>Documentation</h3>
                    <div class="javadoc">
        """
        
        if method.java_doc:
            html_content += f"<pre>{self._escape_html(method.java_doc)}</pre>"
        else:
            html_content += "<p><em>No documentation available</em></p>"
        
        html_content += """
                    </div>
                </div>
                
                <div class="method-code-section">
                    <h3>Source Code</h3>
                    <pre class="code"><code>"""
        
        html_content += self._escape_html(method.code)
        
        html_content += """</code></pre>
                </div>
                
                <div class="outgoing-methods-section">
                    <h3>Called Methods</h3>
        """
        
        if method.dst_methods:
            html_content += "<ul class='outgoing-method-list'>"
            for dst_method in method.dst_methods:
                # Try to find if we have this method in our data
                target_method = self.data.get_method_by_name(
                    type('MethodSource', (), {
                        'class_name': dst_method.class_name,
                        'method_name': dst_method.method_name
                    })()
                )
                
                if target_method:
                    target_id = self._get_method_id(dst_method.class_name, dst_method.method_name)
                    html_content += f"""
                        <li><a href="#{target_id}" class="outgoing-method-link">{self._escape_html(dst_method.class_name)}.{self._escape_html(dst_method.method_name)}</a></li>
                    """
                else:
                    html_content += f"""
                        <li class="external-method">{self._escape_html(dst_method.class_name)}.{self._escape_html(dst_method.method_name)} <em>(external)</em></li>
                    """
            html_content += "</ul>"
        else:
            html_content += "<p><em>No outgoing method calls</em></p>"
        
        html_content += """
                </div>
            </div>
        </section>
        """
        
        return html_content
    
    def _generate_css(self) -> str:
        """Generate CSS styles for the HTML."""
        return """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
                line-height: 1.6;
            }
            
            .container {
                display: flex;
                min-height: 100vh;
            }
            
            .navigation {
                width: 300px;
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                overflow-y: auto;
                position: fixed;
                height: 100vh;
                box-sizing: border-box;
            }
            
            .navigation h2 {
                margin-top: 0;
                color: #ecf0f1;
                border-bottom: 2px solid #34495e;
                padding-bottom: 10px;
            }
            
            .package {
                margin-bottom: 20px;
            }
            
            .package-name {
                color: #e74c3c;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            
            .class-list {
                list-style: none;
                padding-left: 20px;
                margin: 0;
            }
            
            .class-list li {
                margin-bottom: 5px;
            }
            
            .class-link {
                color: #3498db;
                text-decoration: none;
                transition: color 0.3s;
            }
            
            .class-link:hover {
                color: #5dade2;
                text-decoration: underline;
            }
            
            .main-content {
                margin-left: 300px;
                padding: 20px;
                flex: 1;
                background-color: white;
            }
            
            .class-section, .method-section {
                margin-bottom: 40px;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .class-title, .method-title {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 0;
            }
            
            .full-class-name, .method-class {
                color: #7f8c8d;
                font-style: italic;
                margin-bottom: 20px;
            }
            
            .class-content, .method-content {
                display: grid;
                gap: 20px;
            }
            
            .javadoc-section, .code-section, .methods-section,
            .method-javadoc-section, .method-code-section, .outgoing-methods-section {
                border: 1px solid #ecf0f1;
                border-radius: 5px;
                padding: 15px;
                background-color: #fafafa;
            }
            
            .javadoc-section h3, .code-section h3, .methods-section h3,
            .method-javadoc-section h3, .method-code-section h3, .outgoing-methods-section h3 {
                margin-top: 0;
                color: #34495e;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
            }
            
            .javadoc {
                background-color: #fff;
                padding: 10px;
                border-radius: 3px;
                border-left: 4px solid #3498db;
            }
            
            .code {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                font-family: 'Courier New', Consolas, monospace;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .method-list, .outgoing-method-list {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .method-list li, .outgoing-method-list li {
                margin-bottom: 8px;
                padding: 8px;
                background-color: white;
                border-radius: 3px;
                border-left: 3px solid #3498db;
            }
            
            .method-link, .outgoing-method-link {
                color: #2980b9;
                text-decoration: none;
                font-weight: bold;
            }
            
            .method-link:hover, .outgoing-method-link:hover {
                color: #3498db;
                text-decoration: underline;
            }
            
            .external-method {
                color: #95a5a6;
                font-style: italic;
            }
            
            /* Smooth scrolling */
            html {
                scroll-behavior: smooth;
            }
            
            /* Highlight target elements */
            :target {
                animation: highlight 2s ease-in-out;
            }
            
            @keyframes highlight {
                0% { background-color: #f39c12; }
                100% { background-color: transparent; }
            }
        </style>
        """
    
    def generate_html(self, output_file: str = "java_documentation.html"):
        """Generate the complete HTML documentation."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Java Code Documentation</title>
    {self._generate_css()}
</head>
<body>
    <div class="container">
        {self._generate_navigation()}
        
        <main class="main-content">
            <h1>Java Code Documentation</h1>
            
            <!-- Class Sections -->
        """
        
        # Generate class sections
        for java_class in self.data.classes:
            html_content += self._generate_class_section(java_class)
        
        # Generate method sections
        for method in self.data.methods:
            html_content += self._generate_method_section(method)
        
        html_content += """
        </main>
    </div>
</body>
</html>
        """
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML documentation generated: {output_file}")


def generate_java_documentation(java_code_data: JavaCodeData, output_file: str = "java_documentation.html"):
    """
    Generate HTML documentation from JavaCodeData.
    
    Args:
        java_code_data: The JavaCodeData instance containing all the code information
        output_file: The output HTML file name (default: "java_documentation.html")
    """
    generator = JavaCodeHTMLGenerator(java_code_data)
    generator.generate_html(output_file)

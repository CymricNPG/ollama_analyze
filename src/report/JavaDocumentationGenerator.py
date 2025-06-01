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
from collections import defaultdict
from typing import Dict
from pathlib import Path

def escape(s):
    return html.escape(s, quote=False)

def get_package(class_name):
    if '.' in class_name:
        return '.'.join(class_name.split('.')[:-1])
    else:
        return '(default package)'

def class_anchor(class_name):
    return f'class_{class_name.replace(".", "_")}'

def method_anchor(class_name, method_name):
    return f'method_{class_name.replace(".", "_")}__{method_name}'

def generate_html(java_code_data, out_path):
    # Organize classes by package
    packages: Dict[str, list] = defaultdict(list)
    for cls in java_code_data.classes:
        pkg = get_package(cls.class_name)
        packages[pkg].append(cls)

    # Pre-index methods for quick lookup
    methods_by_class: Dict[str, list] = defaultdict(list)
    method_by_fqn: Dict[str, object] = {}
    for method in java_code_data.methods:
        methods_by_class[method.src.class_name].append(method)
        fqn = (method.src.class_name, method.src.method_name)
        method_by_fqn[fqn] = method

    # Start HTML
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="UTF-8">',
        '<title>Java Documentation</title>',
        '<style>',
        'body { font-family: Arial, sans-serif; margin: 0 2em; background: #fafbfc; }',
        '.menu { background: #222d; padding: 1em; border-radius: 8px; margin:1em 0; }',
        '.package { font-weight: bold; margin-top:1em; }',
        '.class-link, .method-link { text-decoration: none; color: #2d66be; cursor:pointer;}',
        '.class-section, .method-section { margin:2em 0; padding:1em; border-radius: 7px; background: #fff; border:1px solid #eee;}',
        '.class-title { font-size: 1.5em; margin-bottom: .2em;}',
        '.block { margin:.5em 0 1em .5em; background:#f5f7fa; border-radius:3px; padding:.8em; border:1px solid #e2e6ea;}',
        '.code {display:block; background:#24292f; color:#fafbfc; font-family:monospace; white-space:pre; border-radius:5px; padding:.7em; margin-top:.4em; font-size: 1em;}',
        '.methods-list { margin-left: 1.5em;}',
        '.method-table { border-collapse: collapse; width:90%; }',
        '.method-table th, .method-table td { border: 1px solid #ccc; padding:.3em .7em;}',
        '.out-list { margin:.2em 0 0 .7em; }',
        '.method-title { font-size:1.2em; }',
        '.section-sep {border-top:1px solid #d2d5d8; margin:2em 0;}',
        '.method-link:hover { text-decoration:underline; }',
        '</style>',
        '</head>',
        '<body>',
        '<h1>Java Documentation Overview</h1>',
        '<nav class="menu">',
        '<strong>Classes by Package:</strong>',
        '<ul>'
    ]
    # Navigation menu
    for pkg in sorted(packages):
        html_parts.append(f'<li class="package">{escape(pkg)}<ul>')
        for cls in sorted(packages[pkg], key=lambda c: c.class_name):
            html_parts.append(
                f'<li><a class="class-link" href="#{class_anchor(cls.class_name)}">{escape(cls.class_name)}</a></li>'
            )
        html_parts.append('</ul></li>')
    html_parts.append('</ul>')
    html_parts.append('</nav>')
    html_parts.append('<hr>')

    # Class sections
    for pkg in sorted(packages):
        for cls in sorted(packages[pkg], key=lambda c: c.class_name):
            html_parts.append(f'<section class="class-section" id="{class_anchor(cls.class_name)}">')
            html_parts.append(f'<div class="class-title">{escape(cls.class_name)}</div>')
            # Javadoc
            html_parts.append('<div class="block"><strong>Javadoc:</strong><br>')
            if cls.java_doc:
                html_parts.append(f'<div>{escape(cls.java_doc)}</div>')
            else:
                html_parts.append('<i>No Javadoc available</i>')
            html_parts.append('</div>')
            # Code
            html_parts.append('<div class="block"><strong>Source code:</strong>')
            html_parts.append(f'<pre class="code">{escape(cls.code)}</pre>')
            html_parts.append('</div>')
            # Methods summary
            methods = methods_by_class.get(cls.class_name, [])
            if methods:
                html_parts.append('<div class="block"><strong>Methods:</strong>')
                html_parts.append('<table class="method-table"><tr><th>Method</th><th>Javadoc</th></tr>')
                for method in sorted(methods, key=lambda m: m.src.method_name):
                    method_id = method_anchor(cls.class_name, method.src.method_name)
                    # Show first line of javadoc (if present)
                    jdoc_summary = (method.java_doc.splitlines()[0] if method.java_doc else '')
                    html_parts.append(f'<tr><td><a class="method-link" href="#{method_id}">{escape(method.src.method_name)}</a></td><td>{escape(jdoc_summary)}</td></tr>')
                html_parts.append('</table>')
                html_parts.append('</div>')
            else:
                html_parts.append('<div class="block"><strong>No methods in this class.</strong></div>')

            html_parts.append('</section><div class="section-sep"></div>')

    # Method sections
    html_parts.append('<h2 id="methods_overview">Methods Details</h2>')
    for key in sorted(method_by_fqn.keys()):
        class_name, method_name = key
        method = method_by_fqn[key]
        section_id = method_anchor(class_name, method_name)
        html_parts.append(f'<section class="method-section" id="{section_id}">')
        html_parts.append(f'<div class="method-title">{escape(class_name)}.<b>{escape(method_name)}</b></div>')
        # Javadoc
        html_parts.append('<div class="block"><strong>Javadoc:</strong><br>')
        if method.java_doc:
            html_parts.append(f'<div>{escape(method.java_doc)}</div>')
        else:
            html_parts.append('<i>No Javadoc available</i>')
        html_parts.append('</div>')
        # Method code
        html_parts.append('<div class="block"><strong>Method code:</strong>')
        html_parts.append(f'<pre class="code">{escape(method.code)}</pre>')
        html_parts.append('</div>')
        # Outgoing methods
        if method.dst_methods:
            html_parts.append('<div class="block"><strong>Outgoing Methods (calls):</strong><ul class="out-list">')
            for out in method.dst_methods:
                out_id = method_anchor(out.class_name, out.method_name)
                html_parts.append(
                    f'<li><a class="method-link" href="#{out_id}">{escape(out.class_name)}.{escape(out.method_name)}</a></li>'
                )
            html_parts.append('</ul></div>')
        else:
            html_parts.append('<div class="block"><strong>No outgoing methods.</strong></div>')

        html_parts.append('</section>')

    html_parts.append('</body></html>')

    # Write HTML to file
    Path(out_path).write_text('\n'.join(html_parts), encoding='utf-8')
    print(f'HTML documentation written to {out_path}')

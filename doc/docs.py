#! /usr/bin/env python

import glob
import re
import shutil
import string
import transform
import os
import os.path

TEMPLATE_DIRECTORY = "template"
OUTPUT_DIRECTORY   = "html"
TUTORIAL_DIRECTORY = "tutorial"
DEMO_DIRECTORY = "demo"
CXX_EXTENSION = "cc"

templates = {}

def load_templates():
    listing = os.listdir(TEMPLATE_DIRECTORY)

    for file in listing:
        title = os.path.splitext(file)[0]
        stream = open(os.path.join(TEMPLATE_DIRECTORY, file))

        try:
            templates[title] = stream.read()
        finally:
            stream.close()

def apply_template(template, args = {}, lax = False, **kwargs):
    if not lax:
        return string.Template(template).substitute(args, **kwargs)
    else:
        return string.Template(template).safe_substitute(args, **kwargs)

def scrub_comments(text):
    return re.sub("<!--([^-]|-[^-]|--[^>])*(-->|$)", "",
                  text, flags = re.DOTALL)

def path_to_html(relative_path):
    return os.path.splitext(relative_path)[0] + ".html"

def path_to_md(relative_path):
    return os.path.splitext(relative_path)[0] + ".md"

def path_to_output(relative_path):
    path = os.path.join(OUTPUT_DIRECTORY, templates["version"], relative_path)

    directory = os.path.dirname(path)
    if not os.path.lexists(directory):
        os.makedirs(directory)

    return path

def remove_output_directory():
    path = os.path.join(OUTPUT_DIRECTORY, templates["version"])
    if os.path.lexists(path):
        shutil.rmtree(path)

def compose_page(relative_path, definitions):
    definitions.update(templates)

    html_file = path_to_html(relative_path)

    if html_file == "index.html":
        canonical = templates["location"]
        definitions["title"] = \
          definitions["project"] + " - " + definitions["title"]
    else:
        canonical = os.path.join(templates["location"], "current", html_file)

    prefix = re.sub("[^/]+", r"..", os.path.split(relative_path)[0])
    if len(prefix) > 0:
        prefix += "/"

    definitions["canonical"] = canonical
    definitions["prefix"] = prefix

    text = templates["page"]
    text = scrub_comments(text)

    while '$' in text:
        text = apply_template(text, definitions)
        text = scrub_comments(text)

    text = "<!-- Automatically generated - edit the templates! -->\n\n" + text

    return text

def write_page(relative_path, text):
    html_file = path_to_html(relative_path)
    path = path_to_output(html_file)

    stream = open(path, "w")
    try:
        stream.write(text)
    finally:
        stream.close()

def copy_static_file(relative_path):
    output_path = path_to_output(relative_path)
    shutil.copy(relative_path, output_path)

def read_extended_markdown(relative_path):
    md_file = path_to_md(relative_path)

    stream = open(md_file)
    try:
        text = stream.read()
        return transform.to_html(text)
    finally:
        stream.close()

def compose_general_page(relative_path):
    definitions = read_extended_markdown(relative_path)
    text = compose_page(relative_path, definitions)
    write_page(relative_path, text)

def list_general_pages():
    return glob.glob("*.md")

def process_threaded(directory):
    sources = glob.glob(os.path.join(directory, "*.md"))

    contents = []
    for file in sources:
        definitions = read_extended_markdown(file)

        title_components = re.split("[ -]+", definitions["title"])
        title_components = map(lambda s: s.capitalize(), title_components)
        html_title = "".join(title_components)
        html_title = filter(lambda c: c not in ",!:-", html_title)
        html_file = os.path.join(directory, html_title + ".html")

        source_file = \
          os.path.splitext(os.path.basename(file))[0] + "." + CXX_EXTENSION
        source_link = "$repo/blob/$version/example/" + source_file

        definitions[directory + "_body"] = definitions["body"]
        definitions["body"] = templates[directory]
        definitions["source"] = source_link

        contents.append((definitions["title"], html_file, definitions))

    index = 0
    for title, html_file, definitions in contents:
        if index < len(contents) - 1:
            next_title, next_file, _ = contents[index + 1]
            definitions["computed_next"] = templates["next"]
            definitions["next_link"] = next_file
            definitions["next_title"] = next_title
        else:
            definitions["computed_next"] = templates["last"]

        text = compose_page(html_file, definitions)
        write_page(html_file, text)

        index += 1

    text = ""
    for title, html_file, _ in contents:
        item = apply_template(templates["tocitem"], {}, True,
                              link = html_file, title = title)
        text += item + "\n"

    templates[directory + "_toc"] = text

def main():
    load_templates()

    remove_output_directory()

    process_threaded(TUTORIAL_DIRECTORY)
    process_threaded(DEMO_DIRECTORY)

    general_pages = list_general_pages()
    for page in general_pages:
        compose_general_page(page)

    copy_static_file("better-enums.css")

if __name__ == "__main__":
    main()

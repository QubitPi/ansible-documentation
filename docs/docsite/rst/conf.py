# -*- coding: utf-8 -*-
#
# documentation build configuration file, created by
# sphinx-quickstart on Sat Sep 27 13:23:22 2008-2009.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed
# automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import os
import tomllib
from pathlib import Path

from sphinx.application import Sphinx

DOCS_ROOT_DIR = Path(__file__).parent.resolve()

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
# sys.path.append(os.path.abspath('some/directory'))
#
sys.path.insert(0, os.path.join('ansible', 'lib'))

# We want sphinx to document the ansible modules contained in this repository,
# not those that may happen to be installed in the version
# of Python used to run sphinx.  When sphinx loads in order to document,
# the repository version needs to be the one that is loaded:
sys.path.insert(0, os.path.abspath(os.path.join('..', '..', '..', 'lib')))

KNOWN_TAGS = {'all', 'ansible', 'core', 'core_lang'}

applied_tags_count = sum(
    int(tags.has(known_tag_name)) for known_tag_name in KNOWN_TAGS
)
assert applied_tags_count == 1, (
    'Exactly one of the following tags expected: {tags}'.
    format(tags=", ".join(KNOWN_TAGS))
)

VERSION = (
     # Controls branch version for core releases
    'devel' if tags.has('core_lang') or tags.has('core') else
    # Controls branch version for Ansible package releases
    'devel' if tags.has('ansible') or tags.has('all')
    else '<UNKNOWN>'
)
AUTHOR = 'Ansible, Inc'


# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings.
# They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
# TEST: 'sphinxcontrib.fulltoc'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'notfound.extension',
    'sphinx_antsibull_ext',  # provides CSS for the plugin/module docs generated by antsibull
    'sphinx_copybutton',
]

# Later on, add 'sphinx.ext.viewcode' to the list if you want to have
# colorized code generated too for references.


# Add any paths that contain templates here, relative to this directory.
templates_path = ['../.templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
root_doc = master_doc = 'index'  # Sphinx 4+ / 3-

# General substitutions.
project = (
    'Ansible Core' if (
        tags.has('all') or tags.has('core_lang') or tags.has('core')
    ) else 'Ansible' if tags.has('ansible')
    else '<UNKNOWN>'
)

copyright = "Ansible project contributors"

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
version = VERSION
# The full version, including alpha/beta/rc tags.
release = VERSION

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
# unused_docs = []

# List of directories, relative to source directories, that shouldn't be
# searched for source files.
# exclude_dirs = []

# A list of glob-style patterns that should be excluded when looking
# for source files.
exclude_patterns = [] if tags.has('all') else [
    'ansible_index.rst',
    'core_index.rst',
]
exclude_patterns += [] if tags.has('all') else [
    'network',
    'scenario_guides',
    'community/collection_contributors/test_index.rst',
    'community/collection_contributors/collection_integration_about.rst',
    'community/collection_contributors/collection_integration_updating.rst',
    'community/collection_contributors/collection_integration_add.rst',
    'community/collection_contributors/collection_test_pr_locally.rst',
    'community/collection_contributors/collection_integration_tests.rst',
    'community/collection_contributors/collection_integration_running.rst',
    'community/collection_contributors/collection_package_removal.rst',
    'community/collection_contributors/collection_reviewing.rst',
    'community/collection_contributors/collection_requirements.rst',
    'community/collection_contributors/collection_unit_tests.rst',
    'community/maintainers.rst',
    'community/contributions_collections.rst',
    'community/create_pr_quick_start.rst',
    'community/reporting_collections.rst',
    'community/contributing_maintained_collections.rst',
    'community/collection_development_process.rst',
    'community/collection_contributors/collection_release_without_branches.rst',
    'community/collection_contributors/collection_release_with_branches.rst',
    'community/collection_contributors/collection_releasing.rst',
    'community/maintainers_guidelines.rst',
    'community/maintainers_workflow.rst',
    'community/steering/community_steering_committee.rst',
    'community/steering/community_topics_workflow.rst',
    'community/steering/steering_committee_membership.rst',
    'community/steering/steering_committee_past_members.rst',
    'community/steering/steering_index.rst',
    'dev_guide/ansible_index.rst',
    'dev_guide/core_index.rst',
    'dev_guide/platforms/aws_guidelines.rst',
    'dev_guide/platforms/openstack_guidelines.rst',
    'dev_guide/platforms/ovirt_dev_guide.rst',
    'dev_guide/platforms/vmware_guidelines.rst',
    'dev_guide/platforms/vmware_rest_guidelines.rst',
    'getting_started_ee/build_execution_environment.rst',
    'getting_started_ee/index.rst',
    'getting_started_ee/introduction.rst',
    'getting_started_ee/run_community_ee_image.rst',
    'getting_started_ee/run_execution_environment.rst',
    'getting_started_ee/setup_environment.rst',
    'porting_guides/porting_guides.rst',
    'porting_guides/porting_guide_[1-9]*',
    'roadmap/index.rst',
    'roadmap/ansible_roadmap_index.rst',
    'roadmap/old_roadmap_index.rst',
    'roadmap/ROADMAP_2_5.rst',
    'roadmap/ROADMAP_2_6.rst',
    'roadmap/ROADMAP_2_7.rst',
    'roadmap/ROADMAP_2_8.rst',
    'roadmap/ROADMAP_2_9.rst',
    'roadmap/COLLECTIONS*'
] if tags.has('core_lang') or tags.has('core') else [
    'porting_guides/core_porting_guides',
] if tags.has('ansible') else '<UNKNOWN>'

nitpick_ignore_regex = [
    (r"py:.*", r"ansible\.(?:.*\.)?_internal\..*"),
]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'ansible'

highlight_language = 'YAML+Jinja'

# Substitutions, variables, entities, & shortcuts for text which do not need to link to anything.
# For titles which should be a link, use the intersphinx anchors set at the index, chapter, and section levels, such as  qi_start_:
# |br| is useful for formatting fields inside of tables
# |_| is a nonbreaking space; similarly useful inside of tables
rst_epilog = """
.. |br| raw:: html

   <br>
.. |_| unicode:: 0xA0
    :trim:
"""


# Options for HTML output
# -----------------------

html_theme_path = []
html_theme = 'sphinx_ansible_theme'
html_show_sphinx = False

html_theme_options = {
    'canonical_url': "https://docs.ansible.com/ansible/latest/",
    'hubspot_id': '330046',
    'satellite_tracking': True,
    'show_extranav': True,
    'tag_manager_id': 'GTM-PSB293',
    'vcs_pageview_mode': 'edit'
}

html_context = {
    'display_github': 'True',
    'show_sphinx': False,
    'is_eol': False,
    'github_user': 'ansible',
    'github_repo': 'ansible-documentation',
    'github_version': 'devel',
    'github_rst_path': 'docs/docsite/rst/',
    'github_template_path': 'docs/templates/',
    'github_root_dir': 'devel/lib/ansible',
    'github_cli_repo': 'ansible',
    'github_cli_version': 'devel',
    'current_version': version,
    'latest_version': (
        'devel' if tags.has('all') else
        '2.19' if tags.has('core_lang') or tags.has('core') else
        '11' if tags.has('ansible')
        else '<UNKNOWN>'
    ),
    # list specifically out of order to make latest work
    'available_versions': (
        ('devel',) if tags.has('all') else
        ('2.15_ja', '2.14_ja', '2.13_ja',) if tags.has('core_lang') else
        ('2.19', '2.18', '2.17', 'devel',) if tags.has('core') else
        ('latest', 'devel') if tags.has('ansible')
        else '<UNKNOWN>'
    ),
}


# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
# html_style = 'solar.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = (
    'Ansible Core Documentation' if (
        tags.has('all') or tags.has('core_lang') or tags.has('core')
    ) else 'Ansible Community Documentation' if tags.has('ansible')
    else '<UNKNOWN>'
)

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = 'Community Documentation'

# The name of an image file (within the static path) to place at the top of
# the sidebar.
# html_logo =

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = 'favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['../_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_use_modindex = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = 'https://docs.ansible.com/ansible/latest'

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'Poseidodoc'

# Configuration for sphinx-notfound-pages
# with no 'notfound_template' and no 'notfound_context' set,
# the extension builds 404.rst into a location-agnostic 404 page
#
# setting explicitly - docsite serves up /ansible/latest/404.html
# so keep this set to `latest` even on the `devel` branch
# then no maintenance is needed when we branch a new stable_x.x
notfound_urls_prefix = "/ansible/latest/"

# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
# latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
# latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class
# [howto/manual]).
latex_documents = [
    (
        'index', 'ansible.tex', 'Ansible Documentation', AUTHOR, 'manual',
    ) if tags.has('core_lang') else (
        'index', 'ansible.tex', 'Ansible 2.2 Documentation', AUTHOR, 'manual',
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# Additional stuff for the LaTeX preamble.
# latex_preamble = ''

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_use_modindex = True

autoclass_content = 'both'

# Note:  Our strategy for intersphinx mappings is to have the upstream build location as the
# canonical source.
intersphinx_mapping = {
    'python': ('https://docs.python.org/2/', None),
    'python3': ('https://docs.python.org/3/', None),
    'jinja2': ('http://jinja.palletsprojects.com/', None),
    'ansible_2_9': ('https://docs.ansible.com/ansible/2.9/', None),
    'ansible_11': ('https://docs.ansible.com/ansible/11/', None),
}

# linckchecker settings
linkcheck_ignore = [
]
linkcheck_workers = 25
# linkcheck_anchors = False

# Generate redirects for pages when building on Read The Docs
def setup(app: Sphinx) -> dict[str, bool | str]:

    if 'redirects' in app.tags:

        redirects_config_path = DOCS_ROOT_DIR.parent / "declarative-configs" / "ansible_redirects.toml"
        redirects = tomllib.loads(redirects_config_path.read_text())
        redirect_template = DOCS_ROOT_DIR.parent / ".templates" / "redirect_template.html"

        app.config.redirects = redirects
        app.config.redirect_html_template_file = redirect_template
        app.setup_extension('sphinx_reredirects') # redirect pages that have been restructured or removed

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "version": app.config.release,
    }

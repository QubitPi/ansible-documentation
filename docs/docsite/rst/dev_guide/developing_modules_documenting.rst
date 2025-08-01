.. _developing_modules_documenting:
.. _module_documenting:

*******************************
Module format and documentation
*******************************

In most cases if you want to contribute your module to an Ansible collection, you should write your module in Python and follow the standard format described below. If you are writing a Windows module, you should follow the :ref:`Windows guidelines <developing_modules_general_windows>`.

Before you open a pull request, in addition to following these guidelines, please also review and adhere to the practices outlined in the following sections:

* :ref:`submission checklist <developing_modules_checklist>`
* :ref:`programming tips <developing_modules_best_practices>`
* :ref:`testing <developing_testing>` before you open a pull request

Every Ansible module written in Python must begin with seven standard sections in a particular order, followed by the code. The sections in order are:

.. contents::
   :depth: 1
   :local:

If you are curious why ``imports`` are not located at the top of the file, see the :ref:`python_imports` section.

If you see any discrepancies in older Ansible modules, please open a pull request with modifications that satisfy these guidelines. 

Non-Python modules documentation
================================

For modules written in languages other than Python, there are two approaches to handling documentation:

* Option one: Create a ``.py`` file that contains the documentation-related sections described in this document.
* Option two: Create a ``.yml`` file that has the same data structure in pure YAML.

  * With YAML files, the examples below are easy to use by removing Python quoting and substituting ``=`` for ``:``, for example ``DOCUMENTATION = r''' ... '''`` to ``DOCUMENTATION: ...`` and removing closing quotes. Refer to :ref:`adjacent_yaml_doc` for details.

.. _shebang:

Python shebang & UTF-8 coding
=============================

1. Begin your Ansible module with the ``#!/usr/bin/python`` shebang so that ``ansible_python_interpreter`` works.

  * If you develop the module using a different scripting language, adjust the interpreter accordingly (``#!/usr/bin/<interpreter>``) so ``ansible_<interpreter>_interpreter`` can work for that specific language.
  * Binary modules do NOT require a shebang or an interpreter.
  * Do NOT use ``#!/usr/bin/env`` because it makes ``env`` the interpreter and bypasses ``ansible_<interpreter>_interpreter`` logic.
  * Passing arguments to the interpreter in the shebang does not work; for example, ``#!/usr/bin/env python``.

2. Follow the shebang immediately with ``# -*- coding: utf-8 -*-`` to clarify that the file is UTF-8 encoded.

.. _copyright:

Copyright and license
=====================

* After the shebang and UTF-8 encoding lines, add a `copyright line <https://www.linuxfoundation.org/blog/copyright-notices-in-open-source-software-projects/>`_ with the original copyright holder and a license declaration.
* The license declaration should be one line ONLY, not the full GPL prefix, as follows:

.. code-block:: python

    #!/usr/bin/python
    # -*- coding: utf-8 -*-

    # Copyright: Contributors to the Ansible project
    # GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

* Additions to the module MUST NOT include additional copyright lines beyond the default statement, unless the default copyright statement is missing.

.. code-block:: python

    # Copyright: Contributors to the Ansible project

* Any legal review will include the source control history, so an exhaustive copyright header is not necessary.
* Please do NOT include a copyright year.

  * If the existing copyright statement includes a year, do NOT edit the existing copyright year.

* Do NOT modify the existing copyright header without permission from the copyright author.

.. _documentation_block:

DOCUMENTATION block
===================

Before committing your module documentation, please test it at the :ref:`command line and as HTML <dev_testing_module_documentation>`.

After the shebang, the UTF-8 encoding, the copyright line, and the license section comes the ``DOCUMENTATION`` block. Ansible's online module documentation is generated from the ``DOCUMENTATION`` blocks in the source code of each module.

The ``DOCUMENTATION`` block must be valid YAML. To make it easier:

* Start by copying our `example documentation string <https://github.com/ansible/ansible-documentation/blob/devel/examples/DOCUMENTATION.yml>`_.
* Write the block in an :ref:`editor with YAML syntax highlighting <other_tools_and_programs>` before you include it in your Python file.
* If you run into syntax issues that are difficult to resolve, use the `YAML Lint <http://www.yamllint.com/>`_ website to help validate the YAML.

When writing module documentation, take the following statements into consideration:

* Module documentation should briefly and accurately define what each module and option does and how it works with others in the underlying system.
* Module documentation should be written for a broad audience and be easily understood both by experts and non-experts.
* Descriptions should always start with a capital letter and end with a full stop or period. Consistency always helps.
* For password and secret arguments ``no_log=True`` should be set and any example passwords, secrets, or hashes should start with ``EXAMPLE`` to ensure no real passwords and so on are leaked.
* For arguments that seem to contain sensitive information but **do not** contain secrets, such as "password_length", set ``no_log=False`` to disable the warning message.
* If an option is only required in certain conditions, describe those conditions; for example, "Required when I(state=present)."
* If your module allows ``check_mode``, reflect this fact in the documentation.
* To create clear, concise, consistent, and useful documentation, follow the :ref:`style guide <style_guide>`.

Each documentation field is described below.

Documentation fields
--------------------

* All fields in the ``DOCUMENTATION`` block are lower-case.
* All fields are required unless specified otherwise.

:module:

  * The name of the module.
  * Must be the same as the file name, without the ``.py`` extension.

:short_description:

  * A short description which is displayed on the :ref:`list_of_collections` page and ``ansible-doc -l``.
  * The ``short_description`` is displayed by ``ansible-doc -l`` without any category grouping,
    so it needs enough detail to explain the module's purpose without the context of the directory structure in which it lives.
  * Unlike ``description:``, ``short_description`` MUST NOT have a trailing period/full stop.
  * You can use :ref:`Ansible markup <ansible_markup>` in this field.

:description:

  * A detailed description (generally two or more sentences).
  * Each sentence MUST be full: start with a capital letter and end with a period.
  * SHOULD NOT mention the module name.
  * Make use of multiple entries rather than using one long paragraph.
  * MUST NOT quote complete values unless it is required by YAML.
  * You can use :ref:`Ansible markup <ansible_markup>` in this field.

:version_added:

  * This is a string, not a float, and should be quoted to avoid errors.
  * For ``ansible.builtin.*`` modules (included in ``ansible-core``), it is a version of ``ansible-core``, for example, ``version_added: '2.18'``
  * In collections, it MUST be a version of a collection (not the Ansible version) when the module was added, for example, ``version_added: '1.0.0'``.

:author:

  * Name of the module author in the form ``First Last (@GitHubID)``.
  * Use a multi-line list if there is more than one author.
  * Do NOT use quotes unless it is required by YAML.

:deprecated:

  * Marks modules that will be removed in future releases. See also :ref:`module_lifecycle`.

:options:

  * Options are often called "parameters" or "arguments". Because the documentation field is called ``options``, we will use that term.
  * If the module has no options (for example, it is a ``_facts`` module), all you need is one line: ``options: {}``.
  * If your module has options (in other words, accepts arguments), document them thoroughly. For each module option, include:

  :option-name:

    * Name it as a declarative operation (not CRUD) that focuses on the final state, for example ``online:``, rather than ``is_online:``.
    * Make the name consistent with the rest of the module, as well as other modules in the same category.
    * When in doubt, look for other modules to find option names that are used for the same purpose, we like to offer consistency to our users.
    * There is no explicit field ``option-name``. This entry is about the *key* of the option in the ``options`` dictionary.

  :description:

    * Detailed explanation of what this option does. Write it in full sentences that shart with a capital letter and end with a period.
    * The first entry is a description of the option itself; subsequent entries detail its use, dependencies, or format of possible values.
    * Do NOT list the possible values (that's what the ``choices:`` field is for, though it should explain what the values do if they are not obvious).
    * If an option is only sometimes required, describe the conditions. For example, "Required when O(state=present)."
    * Mutually exclusive options MUST be documented as the final sentence on each of the options.
    * You can use :ref:`Ansible markup <ansible_markup>` in this field.

  :required:

    * Only needed if ``true``.
    * If missing, we assume the option is not required.

  :default:

    * If ``required`` is either ``false`` or missing, ``default`` may be specified (assumed ``null`` if missing).
    * Ensure that the default value in the docs matches the default value in the code.
    * The default field MUST NOT be listed as part of the description, unless it requires additional information or conditions.
    * If the option is a boolean value, you can use any of the boolean values recognized by Ansible
      (such as ``true``/``false`` or ``yes``/``no``).  Document booleans as ``true``/``false`` for consistency and compatibility with ansible-lint.

  :choices:

    * List of option values.
    * Do NOT use it if empty.

  :type:

    * Specifies the data type that option accepts, MUST match the ``argument_spec`` dictionary.
    * If an argument is ``type='bool'``, set it to ``type: bool`` and do NOT specify ``choices``.
    * If an argument is ``type='list'``, specify ``elements``.

  :elements:

    * Specifies the data type for list elements in case ``type='list'``.

  :aliases:
    * List of optional name aliases.
    * Generally not needed and not recommended to ensure consistency in the module usage.

  :version_added:

    * Only needed if this option was added after initial module release; in other words, this is greater than the top (module) level ``version_added`` field.
    * This is a string, not a float, for example, for a module in ansible-core this could be ``version_added: '2.18'``.
    * In collections, this MUST be the collection version the option was added to, not the Ansible version. For example, ``version_added: '1.0.0'``.

  :suboptions:

    * If this option takes a dict or list of dicts, you can define the structure here.
    * See :ansplugin:`azure.azcollection.azure_rm_securitygroup#module`, :ansplugin:`azure.azcollection.azure_rm_azurefirewall#module`, and :ansplugin:`openstack.cloud.baremetal_node_action#module` for examples.

:requirements:

  * List of requirements (if applicable).
  * Include minimum versions.
  * You can use :ref:`Ansible markup <ansible_markup>` in this field.

:seealso:

  * A list of references to other modules, documentation, or internet resources.
  * Because it is more prominent, use ``seealso`` for general references instead of ``notes`` or adding links to the module ``description``.
  * References to modules MUST use the FQCN or ``ansible.builtin`` for modules in ``ansible-core``.
  * Plugin references are supported since ansible-core 2.15.
  * You can use :ref:`Ansible markup <ansible_markup>` in the ``description`` and ``name`` fields.
  * A reference can be one of the following formats:


    .. code-block:: yaml+jinja

        seealso:

        # Reference by module name
        - module: cisco.aci.aci_tenant

        # Reference by module name, including description
        - module: cisco.aci.aci_tenant
          description: ACI module to create tenants on a Cisco ACI fabric.

        # Reference by plugin name
        - plugin: ansible.builtin.file
          plugin_type: lookup

        # Reference by plugin name, including description
        - plugin: ansible.builtin.file
          plugin_type: lookup
          description: You can use the ansible.builtin.file lookup to read files on the control node.

        # Reference by rST documentation anchor
        - ref: aci_guide
          description: Detailed information on how to manage your ACI infrastructure using Ansible.

        # Reference by rST documentation anchor (with custom title)
        - ref: The official Ansible ACI guide <aci_guide>
          description: Detailed information on how to manage your ACI infrastructure using Ansible.

        # Reference by Internet resource
        - name: APIC Management Information Model reference
          description: Complete reference of the APIC object model.
          link: https://developer.cisco.com/docs/apic-mim-ref/


  * If you use ``ref:`` to link to an anchor that is not associated with a title, you MUST add a title to the ref for the link to work correctly.

:attributes:

  * A dictionary mapping attribute names to dictionaries describing that attribute.
  * Usually attributes are provided by documentation fragments, for example ``ansible.builtin.action_common_attributes`` and its sub-fragments.
    Modules and plugins use the appropriate docs fragments and fill in the ``support``, ``details``, and potential attribute-specific other fields.

  :description:

    * Required.
    * A string or a list of strings. Each string is one paragraph.
    * Explanation of what this attribute does. It should be written in full sentences.
    * You can use :ref:`Ansible markup <ansible_markup>` in this field.

  :details:

    * Generally optional, but must be provided if ``support`` is ``partial``.
    * A string or a list of strings. Each string is one paragraph.
    * Describes how support might not work as expected by the user.
    * You can use :ref:`Ansible markup <ansible_markup>` in this field.

  :support:

    * Required.
    * Must be one of ``full``, ``none``, ``partial``, or ``N/A``.
    * Indicates whether this attribute is supported by this module or plugin.

  :membership:

    * MUST ONLY be provided for the attribute ``action_group``.
    * Lists the action groups this module or action is part of.
    * A string or a list of strings.

  :platforms:

    * MUST ONLY be used for the attribute ``platform``.
    * Lists the platforms the module or action supports.
    * A string or a list of strings.

  :version_added:

    * Only needed if this attribute's support was extended after the module/plugin was created, in other words, this is greater than the top (module) level ``version_added`` field.
    * This is a string, and not a float, for example, ``version_added: '2.3'``.
    * In collections, this must be the collection version the attribute's support was added to, not the Ansible version. For example, ``version_added: '1.0.0'``.

:notes:

  * Details of any important information that does not fit in one of the above sections.
  * Do NOT list ``check_mode`` or ``diff`` information under ``notes``. Use the ``attributes`` field instead.
  * Because it stands out better, use ``seealso`` for general references over the use of ``notes``.
  * You can use :ref:`Ansible markup <ansible_markup>` in this field.

.. _module_docs_fragments:

Documentation fragments
-----------------------

If you are writing multiple related modules, they may share common documentation, such as options, authentication details, file mode settings, ``notes:`` or ``seealso:`` entries. Rather than duplicate that information in each module's ``DOCUMENTATION`` block, you can save it once as a doc_fragment plugin and then include it in each module's documentation.

In Ansible, shared documentation fragments are contained in a ``ModuleDocFragment`` class in `lib/ansible/plugins/doc_fragments/ <https://github.com/ansible/ansible/tree/devel/lib/ansible/plugins/doc_fragments>`_ or in the ``plugins/doc_fragments`` directory in a collection. To include a documentation fragment, add ``extends_documentation_fragment: FRAGMENT_NAME`` in your module documentation. Use the fully qualified collection name for the FRAGMENT_NAME (for example, ``kubernetes.core.k8s_auth_options``).

Modules should only use items from a doc fragment if the module will implement all of the interface documented there in a manner that behaves the same as the existing modules which import that fragment. The goal is that items imported from the doc fragment will behave identically when used in another module that imports the doc fragment.

By default, only the ``DOCUMENTATION`` property from a doc fragment is inserted into the module documentation. It is possible to define additional properties in the doc fragment in order to import only certain parts of a doc fragment or mix and match as appropriate. If a property is defined in both the doc fragment and the module, the module value overrides the doc fragment.

Here is an example doc fragment named ``example_fragment.py``:

.. code-block:: python

    class ModuleDocFragment(object):
        # Standard documentation
        DOCUMENTATION = r'''
        options:
          # options here
        '''

        # Additional section
        OTHER = r'''
        options:
          # other options here
        '''


To insert the contents of ``OTHER`` in a module:

.. code-block:: yaml+jinja

    extends_documentation_fragment: example_fragment.other

Or use both :

.. code-block:: yaml+jinja

    extends_documentation_fragment:
      - example_fragment
      - example_fragment.other

.. versionadded:: 2.8

Since Ansible 2.8, you can have user-supplied doc_fragments by using a ``doc_fragments`` directory adjacent to play or role, just like any other plugin.

For example, all AWS modules should include:

.. code-block:: yaml+jinja

    extends_documentation_fragment:
    - aws
    - ec2

:ref:`docfragments_collections` describes how to incorporate documentation fragments in a collection.

.. _examples_block:

EXAMPLES block
==============

Immediately after the ``DOCUMENTATION`` block comes the ``EXAMPLES`` block. Here you show users how your module works with real-world examples in multi-line plain-text YAML format. The best examples are ready for the user to copy and paste into a playbook. Review and update your examples with every change to your module.

If the module has integration tests, add the example you want to add to the integration tests to make sure it works.

Best practices are:

* Each example should include a ``name:`` line:

.. code-block:: text

    EXAMPLES = r'''
    - name: Ensure foo is installed
      namespace.collection.modulename:
        name: foo
        state: present
    '''

* The ``name:`` line should be capitalized and not include a trailing dot.
* Use a fully qualified collection name (FQCN) as a part of the module's name like in the example above.

  * For modules in ``ansible-core``, use the ``ansible.builtin.`` identifier, for example ``ansible.builtin.debug``.

* If your examples use boolean options, use true/false values. Since the documentation generates boolean values as true/false, having the examples use these values as well makes the module documentation more consistent.
* If your module returns facts that are often needed, consider adding an example of how to use them.

.. _return_block:

RETURN block
============

Right after the ``EXAMPLES`` block comes the ``RETURN`` block. This section documents the information the module returns for use by other modules.

If your module does not return anything (apart from the standard returns made by ansible-core), specify it as ``RETURN = r''' # '''``
Otherwise, for each value returned, provide the following fields. All the fields are required unless specified otherwise:

:return name:
  Name of the returned field.

  :description:
    Detailed description of what this value represents. Capitalized and with a trailing dot.
    You can use :ref:`Ansible markup <ansible_markup>` in this field.
  :returned:
    When this value is returned, such as ``always``, ``changed`` or ``success``. This is a string and can contain any human-readable content.
  :type:
    Data type.
  :elements:
    If ``type='list'``, specifies the data type of the list's elements.
  :sample:
    One or more examples.
  :version_added:
    Only needed if this return was extended after initial module release, in other words, this is greater than the top (module) level ``version_added`` field.
    This is a string, and not a float, for example, ``version_added: '2.3'``.
  :contains:
    Optional. To describe nested return values, set ``type: dict``, or ``type: list``/``elements: dict``, or if you really have to, ``type: complex``, and repeat the elements above for each sub-field.

Here are two example ``RETURN`` sections, one with three simple fields and one with a complex nested field:

.. code-block:: text

    RETURN = r'''
    dest:
        description: Destination file/path.
        returned: success
        type: str
        sample: /path/to/file.txt
    src:
        description: Source file used for the copy on the target machine.
        returned: changed
        type: str
        sample: /home/httpd/.ansible/tmp/ansible-tmp-1423796390.97-147729857856000/source
    md5sum:
        description: MD5 checksum of the file after running copy.
        returned: when supported
        type: str
        sample: 2a5aeecc61dc98c4d780b14b330e3282
    '''

    RETURN = r'''
    packages:
        description: Information about package requirements.
        returned: success
        type: dict
        contains:
            missing:
                description: Packages that are missing from the system.
                returned: success
                type: list
                elements: str
                sample:
                    - libmysqlclient-dev
                    - libxml2-dev
            badversion:
                description: Packages that are installed but at bad versions.
                returned: success
                type: list
                elements: dict
                sample:
                    - package: libxml2-dev
                      version: 2.9.4+dfsg1-2
                      constraint: ">= 3.0"
    '''

.. _python_imports:

Python imports
==============

Immediately after the ``RETURN`` block, add the Python imports. All modules must use Python imports in the form:

.. code-block:: python

   from module_utils.basic import AnsibleModule

The use of "wildcard" imports such as ``from module_utils.basic import *`` is no longer allowed.

.. note:: Why don't the imports go first?

  Since the ``DOCUMENTATION``, ``EXAMPLES``, and ``RETURN`` blocks are essentially extra docstrings for the file and are not used by the module code itself, the import statements are placed after these special variables. Positioning the imports closer to the functional code helps consolidate related elements, improving readability, debugging, and overall comprehension.

.. _dev_testing_module_documentation:

Testing module documentation
============================

* Before committing your module documentation, please test it on the command line and as HTML as described on the :ref:`testing_module_documentation` page.
* To test documentation in collections, please see :ref:`build_collection_docsite`.

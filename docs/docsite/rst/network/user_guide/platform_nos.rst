.. _nos_platform_options:

***************************************
NOS Platform Options
***************************************

Extreme NOS is part of the `community.network <https://galaxy.ansible.com/ui/repo/published/community/network>`_ collection and only supports CLI connections today. ``httpapi`` modules may be added in future.
This page offers details on how to use ``ansible.netcommon.network_cli`` on NOS in Ansible.

.. contents::
  :local:

Connections available
================================================================================

.. table::
    :class: documentation-table

    ====================  ==========================================
    ..                    CLI
    ====================  ==========================================
    Protocol              SSH

    Credentials           uses SSH keys / SSH-agent if present

                          accepts ``-u myuser -k`` if using password

    Indirect Access       by a bastion (jump host)

    Connection Settings   ``ansible_connection: community.netcommon.network_cli``

    |enable_mode|         not supported by NOS

    Returned Data Format  ``stdout[0].``
    ====================  ==========================================

.. |enable_mode| replace:: Enable Mode |br| (Privilege Escalation)

NOS does not support ``ansible_connection: local``. You must use ``ansible_connection: ansible.netcommon.network_cli``.

Using CLI in Ansible
====================

Example CLI ``group_vars/nos.yml``
----------------------------------

.. code-block:: yaml

   ansible_connection: ansible.netcommon.network_cli
   ansible_network_os: community.network.nos
   ansible_user: myuser
   ansible_password: !vault...
   ansible_paramiko_proxy_command: '-o ProxyCommand="ssh -W %h:%p -q bastion01"'


- If you are using SSH keys (including an ssh-agent) you can remove the ``ansible_password`` configuration.
- If you are accessing your host directly (not through a bastion/jump host) you can remove the ``ansible_paramiko_proxy_command`` configuration.
- If you are accessing your host through a bastion/jump host, you cannot include your SSH password in the ``ProxyCommand`` directive. To prevent secrets from leaking out (for example in ``ps`` output), SSH does not support providing passwords through environment variables.

Example CLI task
----------------

.. code-block:: yaml

   - name: Get version information (nos)
     community.network.nos_command:
       commands: "show version"
     register: show_ver
     when: ansible_network_os == 'community.network.nos'


.. include:: shared_snippets/SSH_warning.txt

.. seealso::

       :ref:`timeout_options`

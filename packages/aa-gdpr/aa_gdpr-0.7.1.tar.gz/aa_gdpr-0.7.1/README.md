# AA-GDPR

A Collection of overrides and resources to help Alliance Auth installs meet GDPR legislation.

This Repository cannot guarantee your Legal requirements but aims to reduce the technical burden on Web/System Administrators

## Current Features

Overrides Alliance Auth default resource bundles to use staticfile delivery.

Local staticfile delivery of resources to avoid using CDNs

- Javascript
  - Bootswatch 5.3.3, 5.3.7 Materia Flatly Darkly <http://bootswatch.com>
  - Clipboard.js 2.0.11 <https://clipboardjs.com/>
  - DataTables 1.13.7 , 2.3.2 <http://datatables.net/>
    - DataTables.net-bs5
    - DataTables.bet-bs (Bootstrap 3)
  - jQuery 2.2.4, 3.7.0 <https://github.com/jquery/jquery>
  - jQuery-DateTimePicker 2.5.20 <https://github.com/xdan/datetimepicker>
  - jQuery-UI 1.13.2 <https://jqueryui.com/>
  - Less.js 4.2.0, 4.3.0
  - Moment.js 2.29.4, 2.30.1 <https://github.com/moment/moment>
  - Twitter-Bootstrap 5.3.3, 5.3.7 <https://github.com/twbs/bootstrap>
  - x-editable 1.5.1 <http://vitalets.github.io/x-editable>

- Fonts
  - FontAwesome 5.15.4, 6.4.2 <https://github.com/FortAwesome/Font-Awesome>
  - OFL Lato v16, v24 <https://fonts.google.com/specimen/Lato>
  - OFL Roboto v30, v48 <https://fonts.google.com/specimen/Roboto>
- CSS
  - DataTables 1.10.21, 1.13.7, 2.3.2 <http://datatables.net/>
    - datatables.net-bs5 1.13.7, 2.3.2 <http://datatables.net/>
    - DataTables.bet-bs (Bootstrap 3) bundled with earlier versions of DT
  - FontAwesome 5.11.2, 5.14.0, 5.15.4, 6.7.2 <https://github.com/FortAwesome/Font-Awesome>
  - jQuery-DateTimePicker 2.5.20 <https://github.com/xdan/datetimepicker>
  - jQuery-UI 1.12.1, 1.14.1 <https://jqueryui.com/>
  - x-editable 1.5.1 <http://vitalets.github.io/x-editable>
- AA v4.x Themes
  - Darkly
  - Flatly
  - Materia

## Planned Features

- Consent Management
- Terms of Use Management
- Data Transparency
- Right to be Forgotten Requests

## Installation

### Step One - Install

Install the app with your venv active

```shell
pip install aa-gdpr
```

### Step Two - Configure

- Add the following lines directly before your `INSTALLED_APPS` list in your projects `local.py`

```python
INSTALLED_APPS.insert(0, 'aagdpr')
INSTALLED_APPS.remove('allianceauth.theme.darkly')
INSTALLED_APPS.remove('allianceauth.theme.flatly')
INSTALLED_APPS.remove('allianceauth.theme.materia')
```

- Add the following to `INSTALLED_APPS`

```python
'aagdpr.theme.bootstrap',
'aagdpr.theme.darkly',
'aagdpr.theme.flatly',
'aagdpr.theme.materia',
```

- Add the below lines to your `local.py` settings file

```python
## Settings for AA-GDPR ##

# Instruct third party apps to avoid CDNs
AVOID_CDN = True
DEFAULT_THEME = "aagdpr.theme.flatly.auth_hooks.FlatlyThemeHook"
DEFAULT_THEME_DARK = "aagdpr.theme.darkly.auth_hooks.DarklyThemeHook"  # Legacy AAv3 user.profile.night_mode=1
```

### Step Three - Update Project

- Run migrations `python manage.py migrate` (There should be none yet)
- Gather your staticfiles `python manage.py collectstatic`

## Settings

`AVOID_CDN` - Will attempt to instruct third party applications to attempt to load CSS JS and Fonts from staticfiles, Default `True`.

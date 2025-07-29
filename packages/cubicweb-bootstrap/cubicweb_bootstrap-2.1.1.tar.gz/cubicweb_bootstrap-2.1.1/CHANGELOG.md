## Version 2.1.1 (2025-07-08)

- fix use tags from cube web
- fix support cw under 3.25

## Version 2.1.0 (2025-07-03)
### 🎉 Maintenance of cube's sources

- Python 3.9.2 is now the minimum (included)
- Minimum version of CubicWeb is now 4.5.2 (included)
- Maximum version of CubicWeb is now 5 (included)

## Version 2.0.0 (2023-07-07)
### 🎉 New features

- pkg: upgrade CW minimal version and add cubicweb-web dependence
  *BREAKING CHANGE*: upgrade CW minimal version and add cubicweb-web dependence

### 👷 Bug fixes

- pkg: drop six dependency since it's not used anymore

### 📝 Documentation

- licence: update licence dates

### 🤷 Various changes

- chore(black)

## Version 1.12.0 (2023-05-22)
### 👷 Bug fixes

- xss: Do not format string with the self.w method

## Version 1.11.0 (2023-05-11)
### 👷 Bug fixes

- xss: Do not format string with the self.w method

## Version 1.10.0 (2023-01-20)
### 👷 Bug fixes

- xss: Do not format string with the self.w method

## Version 1.9.0 (2022-11-24)
### 🎉 New features

- cubicweb-3.38: change all cubicweb.web/views to cubicweb_web cube
  *BREAKING CHANGE*: change all cubicweb.web/views to cubicweb_web cube

### 🤖 Continuous integration

- gitlab-ci: use templates from a common repository

## Version 1.8.0 (2022-04-08)
### 🎉 New features

- setup.py: increase cubicweb max version to 3.37.x

## Version 1.7.0 (2022-03-28)
### 🎉 New features

- setup.py: increase cubicweb max version to 3.35.x

## Version 1.6.7 (2021-03-25)
### 👷 Bug fixes

- pkg: correct a typo in the `six` version (O letter vs 0 number)…

## Version 1.6.6 (2021-03-22)
### 👷 Bug fixes

- make the rql completion working again

### 📝 Documentation

- licence: update licence dates

### 🤖 Continuous integration

- gitlab-ci: image: is not longer a global keyword
- integrate pytest-deprecated-warnings

### 🤷 Various changes

- ci: add gitlab-ci
- fix the fix
- Upgrade miscellaneous things
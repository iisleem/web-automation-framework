# Starter Project Template

Use this folder as the first product-specific layer after creating a repository from the web
automation framework template.

This starter follows the shared
[Automation Framework Template Strategy](https://github.com/iisleem/automation-core/blob/main/docs/template_strategy.md)
for keeping framework internals separate from product-owned suite code.

Recommended first steps:

1. Copy the starter folders into the repository root or use them as a reference.
2. Replace `config/environments.yaml` with the product environments.
3. Move product locators into `pages/`.
4. Keep business journeys in `flows/`.
5. Keep tests readable, marker-driven, and free from raw locators.
6. Run `python framework.py doctor`, `python framework.py run --smoke`, and the relevant browser
   matrix before opening a PR.

This folder intentionally contains only the product suite layer. Framework internals, fixtures,
reporting, browser setup, and reusable helpers stay in the framework repository structure.

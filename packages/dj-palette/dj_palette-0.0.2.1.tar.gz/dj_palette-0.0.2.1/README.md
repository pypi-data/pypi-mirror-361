
````md
# 🎨 django-palette

Build beautiful, dynamic Django admin pages using drag-and-drop components.

**django-palette** gives developers and power users the ability to customize Django’s admin interface using a modern layout system, Bootstrap components, and a flexible templating engine — all without losing the power of Django’s permissions and admin tools.

---

## ✨ Features

- 🖼️ Custom `AdminSite` with Bootstrap styling
- ⚙️ Extendable via custom components and template tags
- 🧩 Live-rendered UI components via `{% palette_ui %}`
- 🔧 Drag-and-drop editor (optional, configurable)
- 🔐 Fully supports Django auth and permission system
- 🧠 Works with existing apps and models, zero migration needed

---

## 📦 Installation

```bash
pip install dj-palette
````

---

## ⚙️ Setup

In your `settings.py`, add it above Django's admin so it takes precedence:

```python
INSTALLED_APPS = [
    'dj_palette',  # Must come before 'django.contrib.admin'
    'django.contrib.admin',
    ...
]
```

Then in your `urls.py`, register your custom admin site:

```python
from dj_palette.admin import palette_admin_site
from django.urls import path

urlpatterns = [
    path('admin/', palette_admin_site.urls),
]
```

---

## 🧩 Usage

### Render a UI Component Inline

Render a component directly in a template with props:

```django
{% load palette %}

{% palette_ui "palette/components/card.html" with title="Total Users" content="123" onclick="alert('Hello')" %}
```

### Extend a UI Component Block

Use the block form to add custom HTML below the component:

```django
{% palette_ui "palette/components/card.html" with title="Active Users" %}
  {{ palette_ui.super }}
  <p class="text-muted">More details here...</p>
{% endpalette_ui %}
```

---

## 🛠 Built-in Tags

* `palette_ui` — render and optionally extend a UI component
* `render_ui` — legacy/simple usage to render from a component string
* `back_button` — generates a back URL for the change/add form

---

## 🧱 Custom Components

To create a custom component:

1. Place your component in `templates/palette/components/your_component.html`
2. Use template variables for inputs like `title`, `content`, or `onclick`
3. Render it via `{% palette_ui %}` or `|render_ui` filter

Example: `card.html`

```html
<div class="card">
  <div class="card-body">
    <h5 class="card-title">{{ title }}</h5>
    <p class="card-text">{{ content }}</p>
    {% if onclick %}
      <button onclick="{{ onclick }}" class="btn btn-sm btn-outline-primary">Action</button>
    {% endif %}
  </div>
</div>
```

---

## 🖥️ Admin Pages & Dashboard

Out of the box, `django-palette` replaces the default dashboard and allows you to define new pages like:

* `/admin/dashboard/` → your custom index
* `/admin/pages/<slug>/` → render a saved page layout
* `/admin/pages/edit/<slug>/` → page builder/editor (optional)

These are configured in `dj_palette/admin.py`.

---

## ✏️ Configuration

You can configure UI options using `PALETTE_SETTINGS` in your settings file:

```python
PALETTE_SETTINGS = {
    "site_header": "My Admin",
    "index_title": "Dashboard",
    "custom_links": [
        {
            "label": "Support",
            "url_name": "admin:support_chat",
            "left_icon": "bi bi-chat-dots"
        }
    ],
    "show_editor": True,  # enables drag-and-drop editor
}
```

---

## 🧪 Example Admin Dashboard

```django
{% extends "admin/base_site.html" %}
{% load palette %}

{% block content %}
  <div class="row">
    <div class="col-md-4">
      {% palette_ui "palette/components/card.html" with title="Total Users" content="1000" %}
        {{ palette_ui.super }}
        <p class="small text-muted">Based on active records</p>
      {% endpalette_ui %}
    </div>
  </div>
{% endblock %}
```

---

## 🧩 Upcoming Features

* [ ] Component nesting with slots
* [ ] Live preview in the editor
* [ ] Import/export page layouts as JSON
* [ ] Developer CLI to scaffold components

---

## 🤝 Contributing

Want to contribute? Fork this repo and submit a pull request!

1. Clone the repo
2. Activate your virtualenv and run `pip install -e .`
3. Create your feature branch (`git checkout -b feature/your-feature`)
4. Commit your changes (`git commit -am 'Add cool feature'`)
5. Push and open a PR

---

## 📄 License

MIT License © 2025 \[Your Name or Org]

---

## 📚 Documentation

More docs & examples coming soon at:
**[https://dj-palette.readthedocs.io](https://dj-palette.readthedocs.io)**

Need help? Open an issue or reach out directly.

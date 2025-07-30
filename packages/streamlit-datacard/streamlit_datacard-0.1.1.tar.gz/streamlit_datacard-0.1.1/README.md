# Streamlit DataCard

A responsive card component for displaying structured data in Streamlit applications. Automatically arranges data into a clean grid layout with support for images, badges, custom styling, and interactive clicking.

## Features

- **Card layouts** - Display your data in clean, responsive cards
- **Badge support** - Show categorical data as colored badges with auto-generated colors
- **Image support** - Display images at the top of cards
- **Interactive clicking** - Make cards clickable to build dynamic user interfaces
- **Responsive design** - Automatically adapts to screen size and layout
- **Themeable** - Respects Streamlit's theme settings

## Installation

```bash
pip install streamlit-datacard
```

## Quick Start

```python
import streamlit as st
from streamlit_datacard import datacard

# Sample data
data = [
    {
        "name": "Alice Johnson",
        "role": "Product Manager", 
        "department": "Product",
        "status": "Active",
        "location": "San Francisco"
    },
    {
        "name": "Bob Smith",
        "role": "Software Engineer",
        "department": "Engineering", 
        "status": "Active",
        "location": "New York"
    }
]

# Define which fields should be displayed as badges
field_types = {
    "department": "badge",
    "status": "badge"
}

# Display the datacards
datacard(
    data=data,
    title_field="name",
    field_types=field_types,
    card_width=250,
    max_height=400
)
```

## API Reference

### `datacard(data, **kwargs)`

#### Parameters

- **`data`** *(list of dict, required)*: List of records to display as cards
- **`title_field`** *(str, optional)*: Field name to use as card title
- **`image_field`** *(str, optional)*: Field name containing image URLs
- **`field_types`** *(dict, optional)*: Map field names to display types (`"badge"` or `"text"`)
- **`card_width`** *(int, default 280)*: Width of each card in pixels
- **`max_height`** *(int, default 400)*: Maximum height of cards in pixels
- **`clickable`** *(bool, default False)*: Whether cards are clickable
- **`key`** *(str, optional)*: Unique key for the component

#### Returns

- **`dict or None`**: If `clickable=True`, returns the clicked card's data when a card is clicked. Otherwise returns `None`.

## Examples

### Interactive Employee Directory

```python
import streamlit as st
from streamlit_datacard import datacard

employees = [
    {
        "name": "Alice Johnson",
        "role": "Product Manager",
        "department": "Product",
        "status": "Active",
        "email": "alice@company.com",
        "skills": "Strategy,Leadership,Analytics",
        "image": "https://api.dicebear.com/7.x/personas/svg?seed=Alice"
    },
    {
        "name": "Bob Smith",
        "role": "Software Engineer", 
        "department": "Engineering",
        "status": "Active",
        "email": "bob@company.com",
        "skills": "Python,React,AWS",
        "image": "https://api.dicebear.com/7.x/personas/svg?seed=Bob"
    }
]

field_types = {
    "department": "badge",
    "status": "badge",
    "skills": "badge"
}

# Create two columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Display clickable employee cards
    clicked_employee = datacard(
        data=employees,
        title_field="name",
        image_field="image",
        field_types=field_types,
        clickable=True,
        card_width=200
    )

with col2:
    # Show employee details when clicked
    if clicked_employee:
        st.subheader(f"👤 {clicked_employee['name']}")
        st.write(f"**Role:** {clicked_employee['role']}")
        st.write(f"**Email:** {clicked_employee['email']}")
        
        # Action buttons
        if st.button("📧 Send Email"):
            st.success(f"Email sent to {clicked_employee['name']}!")
        if st.button("📅 Schedule Meeting"):
            st.success(f"Meeting scheduled!")
    else:
        st.info("👈 Click on an employee card to view details")
```

### Simple Task Display

```python
tasks = [
    {
        "task": "Design Homepage",
        "assignee": "Alice Johnson",
        "priority": "High",
        "status": "In Progress",
        "due_date": "2024-01-15"
    },
    {
        "task": "API Integration",
        "assignee": "Bob Smith",
        "priority": "Medium", 
        "status": "Todo",
        "due_date": "2024-01-20"
    }
]

# Non-clickable display
datacard(
    data=tasks,
    title_field="task",
    field_types={"priority": "badge", "status": "badge"},
    card_width=200,
    max_height=250
)
```

## Field Types

- **`"text"`** *(default)*: Display as regular text
- **`"badge"`**: Display as colored badge pills
  - Each unique value gets a consistent color
  - Comma-separated values become multiple badges
  - Colors are automatically generated using a hash function
  - 
## Development

### Setting up for development

```bash
# Clone the repository
git clone https://github.com/your-username/streamlit-datacard
cd streamlit-datacard

# Install in development mode
pip install -e .

# Start the frontend development server
cd streamlit_datacard/frontend
npm install
npm start

# In another terminal, run your Streamlit app
streamlit run example.py
```

### Building for production

```bash
cd streamlit_datacard/frontend
npm run build
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
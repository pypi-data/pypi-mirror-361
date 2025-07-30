import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "streamlit_datacard",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_datacard", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def datacard(data, title_field=None, image_field=None, field_types=None, card_width=280, max_height=400, clickable=False, key=None):
    """Create a datacard component.

    Parameters
    ----------
    data: list of dict
        List of records to display as cards.
    title_field: str, optional
        Field name to use as card title.
    image_field: str, optional
        Field name containing image URLs.
    field_types: dict, optional
        Field types for styling.
    card_width: int, default 280
        Width of each card in pixels.
    max_height: int, default 400
        Maximum height of cards.
    clickable: bool, default False
        Whether cards are clickable.
    key: str or None
        Unique component key.

    Returns
    -------
    dict or None
        If clickable=True, returns the clicked card's data when a card is clicked.
        Otherwise returns None.
    """
    result = _component_func(
        data=data,
        title_field=title_field,
        image_field=image_field,
        field_types=field_types or {},
        card_width=card_width,
        max_height=max_height,
        clickable=clickable,
        key=key,
        default=None
    )
    
    if clickable and result is not None:
        return result
    return None

import kivy
kivy.require('1.9.1')
from kivy.uix.boxlayout import BoxLayout
from kivy.app import Builder
from autosportlabs.racecapture.theme.color import ColorScheme

class SectionBoxLayout(BoxLayout):
    """
    Provides a consistent BoxLayout with some some decoration and padding 
    """
Builder.load_string("""
<SectionBoxLayout>:
    canvas.before:
        Color:
            rgba: ColorScheme.get_dark_background_translucent()
        Rectangle:
            pos: self.pos
            size: self.size             
    padding: (dp(5), dp(5))
    spacing: dp(5)                    
            """)

class HeaderSectionBoxLayout(SectionBoxLayout):
    """
    A header variation of Section box layout with a highlighted background color 
    """
Builder.load_string("""
<HeaderSectionBoxLayout>:
    canvas.before:
        Color:
            rgba: ColorScheme.get_medium_background()
        Rectangle:
            pos: self.pos
            size: self.size             
    
""")

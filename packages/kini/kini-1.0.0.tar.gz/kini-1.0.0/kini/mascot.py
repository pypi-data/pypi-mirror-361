"""
ASCII Mascot for Kini - Your Secret Keeper
"""

KINI_MASCOT = r"""
       ╭─────╮
      │  ◕ ◕  │
      │    ‿   │
      │   |||  │
      ╰─────────╯
        │ │ │
      ┌─┴─┴─┴─┐
      │ KINI  │
      └───────┘
   Your secrets are safe!
"""

KINI_WINK = r"""
      ┌─────────┐
     │  ◕    -  │
     │     ‿     │
     │  \  |  /  │
     └───┬───┬───┘
         │ 🗝 │
      ┌──┴───┴──┐
      │  KINI   │
      └─────────┘
"""

KINI_GUARDIAN = r"""
        ╭─╮ ╭─╮
       │ ◕ ╲╱ ◕ │
       │    ‿    │
      ╱│  \\_//  │╲
     ╱ ╰─────────╯ ╲
    │  🔐 SECRETS 🔐 │
    ╰─────KINI──────╯
"""

KINI_MINI = r"""
    ◕   ◕
      ‿
     /│\
      │
   ┌──┴──┐
   │KINI │
   └─────┘
"""


def show_mascot(style="default"):
    """Display Kini mascot"""
    mascots = {
        "default": KINI_MASCOT,
        "wink": KINI_WINK,
        "guardian": KINI_GUARDIAN,
        "mini": KINI_MINI,
    }
    return mascots.get(style, KINI_MASCOT)


def welcome_message():
    """Welcome message with mascot"""
    return f"""
{KINI_MASCOT}

Welcome to Kini - Your Personal Secret Keeper!
===============================================
I'm here to protect your passwords and keep your secrets safe.
Trust me, your digital life is in good hands! 🔒
"""

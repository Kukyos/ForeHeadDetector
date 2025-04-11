class ModernTheme:
    # Modern color scheme with gradients
    BACKGROUND = '#0a0a0a'  # Deep black
    SECONDARY_BG = '#141414'  # Slightly lighter black
    SIDEBAR_BG = '#1a1a1a'  # Dark sidebar
    TEXT = '#ffffff'  # Pure white
    ACCENT = '#00ff8c'  # Neon green
    ACCENT_DARK = '#00cc71'  # Darker green for hover
    CARD_BG = '#1c1c1c'  # Card background
    HOVER_BG = '#2a2a2a'  # Hover background
    DISABLED = '#404040'  # Disabled state
    DIVIDER = '#333333'  # Divider color
    
    # Enhanced effects
    CORNER_RADIUS = 15  # Increased corner radius
    GLOW_COLOR = (0, 255, 140)  # Neon green RGB
    GLOW_ALPHA = 0.25  # Increased glow transparency
    SHADOW_COLOR = '#000000'
    OPACITY_NORMAL = 0.95  # Normal state opacity
    OPACITY_HOVER = 1.0  # Hover state opacity
    
    # Modern fonts
    TITLE_FONT = ('Segoe UI', 28, 'bold')
    HEADER_FONT = ('Segoe UI', 18, 'bold')
    NORMAL_FONT = ('Segoe UI', 12)
    
    @staticmethod
    def apply_theme(style):
        # Main frame styles
        style.configure('Main.TFrame',
                       background=ModernTheme.BACKGROUND)
        
        # Enhanced sidebar frame - lighter background for better contrast
        style.configure('Sidebar.TFrame',
                       background=ModernTheme.SIDEBAR_BG,
                       relief='flat')
        
        # Content frame
        style.configure('Content.TFrame',
                       background=ModernTheme.BACKGROUND,
                       relief='flat')
        
        # Card frame
        style.configure('Card.TFrame',
                       background=ModernTheme.CARD_BG,
                       relief='flat',
                       borderwidth=0)
        
        # Enhanced button styles with consistent colors
        style.configure('Sidebar.TButton',
                       background=ModernTheme.ACCENT,
                       foreground=ModernTheme.BACKGROUND,
                       font=ModernTheme.NORMAL_FONT,
                       padding=(15, 8),
                       relief='flat',
                       borderwidth=1)
        
        style.map('Sidebar.TButton',
                 background=[('active', ModernTheme.ACCENT_DARK),
                           ('pressed', ModernTheme.ACCENT_DARK)],
                 foreground=[('active', ModernTheme.BACKGROUND),
                           ('pressed', ModernTheme.BACKGROUND)],
                 relief=[('pressed', 'sunken')])
        
        # Label styles with correct backgrounds
        style.configure('Title.TLabel',
                       background=ModernTheme.BACKGROUND,
                       foreground=ModernTheme.TEXT,
                       font=ModernTheme.TITLE_FONT)
        
        style.configure('Subtitle.TLabel',
                       background=ModernTheme.CARD_BG,
                       foreground=ModernTheme.ACCENT,
                       font=ModernTheme.HEADER_FONT)
        
        style.configure('Sidebar.TLabel',
                       background=ModernTheme.SIDEBAR_BG,
                       foreground=ModernTheme.TEXT,
                       font=ModernTheme.NORMAL_FONT)
        
        # Settings styles
        style.configure('Switch.TCheckbutton',
                       background=ModernTheme.CARD_BG,
                       foreground=ModernTheme.TEXT,
                       font=ModernTheme.NORMAL_FONT)
        
        style.configure('Slider.Horizontal.TScale',
                       background=ModernTheme.CARD_BG,
                       troughcolor=ModernTheme.ACCENT_DARK,
                       sliderlength=20,
                       sliderrelief='flat')
        
        # Divider style - more visible
        style.configure('Divider.TSeparator',
                       background=ModernTheme.DIVIDER)
    
    @staticmethod
    def rgb_to_hex(rgb, alpha=1.0):
        """Convert RGB values to hex color with optional alpha"""
        r, g, b = rgb
        hex_color = "#{:02x}{:02x}{:02x}".format(
            min(255, int(r * alpha)),
            min(255, int(g * alpha)),
            min(255, int(b * alpha))
        )
        return hex_color
    
    @staticmethod
    def create_round_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle shape on a canvas"""
        return canvas.create_polygon([
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ], smooth=True, **kwargs)
    
    @staticmethod
    def add_glow_effect(widget, canvas, x, y, width, height):
        """Add a layered glow effect around a widget"""
        base_color = ModernTheme.GLOW_COLOR
        num_layers = 4
        
        # Clear any existing glow effects
        canvas.delete('glow')
        
        # Draw glow layers from outer to inner
        for i in range(num_layers):
            alpha = ModernTheme.GLOW_ALPHA * (1 - (i / num_layers))
            glow_color = ModernTheme.rgb_to_hex(base_color, alpha)
            
            padding = i * 3
            ModernTheme.create_round_rectangle(
                canvas,
                x - padding,
                y - padding,
                x + width + padding,
                y + height + padding,
                ModernTheme.CORNER_RADIUS + padding/2,
                fill=glow_color,
                outline='',
                tags='glow'
            )
    
    @staticmethod
    def create_gradient(canvas, x1, y1, x2, y2, color1, color2):
        """Create a vertical gradient effect"""
        for i in range(y1, y2):
            ratio = (i - y1) / (y2 - y1)
            r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
            g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
            b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(x1, i, x2, i, fill=color)
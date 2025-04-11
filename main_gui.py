import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import subprocess
import sys
import os
from PIL import Image, ImageTk
import cv2
from gui_theme import ModernTheme
import webbrowser

class ModernGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Face Tracking Control Center")
        self.root.geometry("1200x800")
        self.root.configure(bg=ModernTheme.BACKGROUND)
        
        # Remove window title bar and create custom one
        self.root.overrideredirect(True)
        
        # Load config
        self.load_config()
        
        # Create and apply theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        ModernTheme.apply_theme(self.style)
        
        self.create_title_bar()
        self.create_main_interface()
        
        # Add window dragging
        self.bind_drag_events()
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                'display': {
                    'window_width': 1200,
                    'window_height': 800,
                    'sidebar_width': 250,
                    'show_fps': True
                },
                'colors': {
                    'accent': (0, 255, 140),
                    'background': (10, 10, 10),
                    'text': (255, 255, 255)
                }
            }
            self.save_config()

    def save_config(self):
        """Save current configuration to config.json"""
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {str(e)}")
            return False
    
    def create_title_bar(self):
        title_bar = ttk.Frame(self.root, style='Main.TFrame')
        title_bar.pack(fill='x', pady=0)
        
        title = ttk.Label(title_bar, text="Face Tracking Control Center",
                         style='Title.TLabel')
        title.pack(side='left', padx=10)
        
        close_btn = ttk.Button(title_bar, text="×",
                              command=self.root.quit,
                              style='Sidebar.TButton')
        close_btn.pack(side='right')
        
        self.title_bar = title_bar
        
    def bind_drag_events(self):
        self.title_bar.bind('<Button-1>', self.start_drag)
        self.title_bar.bind('<B1-Motion>', self.on_drag)
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def create_main_interface(self):
        # Main container
        main_container = ttk.Frame(self.root, style='Main.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create fixed-width sidebar frame
        self.sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=250)
        self.sidebar.pack(side='right', fill='y')
        self.sidebar.pack_propagate(False)  # Prevent sidebar from shrinking
        
        # Add divider between sidebar and content
        divider = ttk.Separator(main_container, orient='vertical',
                              style='Divider.TSeparator')
        divider.pack(side='right', fill='y')
        
        # Create content area
        content_container = ttk.Frame(main_container, style='Content.TFrame')
        content_container.pack(side='left', fill='both', expand=True)
        
        # Add padding to content area
        self.content_area = ttk.Frame(content_container, style='Content.TFrame')
        self.content_area.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_sidebar_buttons()
        self.show_welcome_screen()

    def create_sidebar_buttons(self):
        # Add navigation header
        header = ttk.Label(self.sidebar,
                          text="Navigation",
                          style='Subtitle.TLabel',
                          background=ModernTheme.SIDEBAR_BG)
        header.pack(pady=(20, 15), padx=15)
        
        # Navigation buttons
        buttons = [
            ("Launch Framework", lambda: self.run_script('forehead_detector.py'), "🚀"),
            ("Games", self.show_games, "🎮"),
            ("Settings", self.show_settings, "⚙️"),
            ("Help", self.show_help, "❓")
        ]
        
        for text, command, icon in buttons:
            # Button container for padding
            btn_container = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
            btn_container.pack(fill='x', padx=10, pady=3)
            
            btn = ttk.Button(btn_container,
                           text=f"{icon}  {text}",
                           command=command,
                           style='Sidebar.TButton')
            btn.pack(fill='x', ipady=5)
            
            # Add divider except for last button
            if text != "Help":
                divider = ttk.Separator(self.sidebar,
                                      orient='horizontal',
                                      style='Divider.TSeparator')
                divider.pack(fill='x', pady=8, padx=20)

    def clear_content(self):
        """Clear all widgets from content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        self.clear_content()
        
        # Create canvas for content and effects
        welcome_canvas = tk.Canvas(self.content_area,
                                 background=ModernTheme.BACKGROUND,
                                 highlightthickness=0,
                                 width=800,
                                 height=600)
        welcome_canvas.pack(fill='both', expand=True)
        
        # Create welcome card with proper background and padding
        welcome_frame = ttk.Frame(welcome_canvas, style='Card.TFrame')
        
        # Position the frame using canvas coordinates
        card_width = 600
        card_height = 300
        x_pos = (800 - card_width) // 2
        y_pos = (600 - card_height) // 2
        
        # Add glow effect before creating window
        ModernTheme.add_glow_effect(welcome_frame, welcome_canvas,
                                   x_pos, y_pos, card_width, card_height)
        
        # Create canvas window for the frame
        welcome_canvas.create_window(x_pos, y_pos,
                                   window=welcome_frame,
                                   width=card_width,
                                   height=card_height,
                                   anchor='nw')
        
        # Add padding container
        content_frame = ttk.Frame(welcome_frame, style='Card.TFrame')
        content_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Welcome content with proper styling and background colors
        title = ttk.Label(content_frame,
                         text="Welcome to Face Tracking",
                         style='Title.TLabel',
                         background=ModernTheme.CARD_BG)
        title.pack()
        
        subtitle = ttk.Label(content_frame,
                           text="Control Center",
                           style='Subtitle.TLabel',
                           background=ModernTheme.CARD_BG)
        subtitle.pack(pady=20)
        
        desc = ttk.Label(content_frame,
                        text="Experience the next generation of face tracking technology",
                        style='Sidebar.TLabel',
                        background=ModernTheme.CARD_BG,
                        wraplength=500,
                        justify='center')
        desc.pack(pady=20)
    
    def show_framework(self):
        self.clear_content()
        
        # Create canvas for content and effects
        framework_canvas = tk.Canvas(self.content_area,
                                   background=ModernTheme.BACKGROUND,
                                   highlightthickness=0,
                                   width=800,
                                   height=600)
        framework_canvas.pack(fill='both', expand=True)
        
        # Create launch card with proper background and padding
        launch_frame = ttk.Frame(framework_canvas, style='Card.TFrame')
        
        # Position frame using canvas coordinates
        card_width = 400
        card_height = 200
        x_pos = (800 - card_width) // 2
        y_pos = (600 - card_height) // 2
        
        # Add glow effect before creating window
        ModernTheme.add_glow_effect(launch_frame, framework_canvas,
                                   x_pos, y_pos, card_width, card_height)
        
        # Create canvas window for the frame
        framework_canvas.create_window(x_pos, y_pos,
                                     window=launch_frame,
                                     width=card_width,
                                     height=card_height,
                                     anchor='nw')
        
        # Add content with proper styling
        title = ttk.Label(launch_frame,
                         text="Face Tracking Framework",
                         style='Title.TLabel',
                         background=ModernTheme.CARD_BG)
        title.pack(pady=(30, 10))
        
        desc = ttk.Label(launch_frame,
                        text="Launch the core face tracking system\n"
                             "with real-time detection and distance estimation",
                        justify='center',
                        style='Sidebar.TLabel',
                        background=ModernTheme.CARD_BG)
        desc.pack(pady=10)
        
        launch_btn = ttk.Button(launch_frame,
                              text="🚀 Launch",
                              command=lambda: self.run_script('forehead_detector.py'),
                              style='Sidebar.TButton')
        launch_btn.pack(pady=20)
        
        # Add hover effect to launch button
        def on_enter(e):
            launch_btn.configure(text="🚀 Start System")
        def on_leave(e):
            launch_btn.configure(text="🚀 Launch")
            
        launch_btn.bind('<Enter>', on_enter)
        launch_btn.bind('<Leave>', on_leave)
    
    def show_games(self):
        self.clear_content()
        
        # Create main canvas for content and effects
        games_canvas = tk.Canvas(self.content_area,
                               background=ModernTheme.BACKGROUND,
                               highlightthickness=0,
                               width=800,
                               height=600)
        games_canvas.pack(fill='both', expand=True)
        
        # Create header with title and subtitle - moved up
        header_frame = ttk.Frame(games_canvas, style='Card.TFrame')
        games_canvas.create_window(400, 30,
                                 window=header_frame,
                                 anchor='n',
                                 width=700)
        
        title = ttk.Label(header_frame,
                         text="Choose Your Game",
                         style='Title.TLabel',
                         background=ModernTheme.CARD_BG)
        title.pack(pady=(20, 5))
        
        subtitle = ttk.Label(header_frame,
                           text="Control games with face tracking",
                           style='Subtitle.TLabel',
                           background=ModernTheme.CARD_BG)
        subtitle.pack(pady=(0, 20))
        
        # Game cards container - moved down
        cards_frame = ttk.Frame(games_canvas, style='Content.TFrame')
        games_canvas.create_window(400, 350,
                                 window=cards_frame,
                                 anchor='center')
        
        games = [
            {
                'title': 'Single Player Pong',
                'desc': 'Challenge the AI in this classic game.\nControl the paddle with your head movements!',
                'script': 'forehead_pong.py',
                'icon': '🎮'
            },
            {
                'title': 'Two Player Pong',
                'desc': 'Face off against a friend in split-screen mode.\nEach player controls their paddle with head movements!',
                'script': 'two_player_pong.py',
                'icon': '👥'
            }
        ]
        
        for i, game in enumerate(games):
            # Create game card
            game_frame = ttk.Frame(cards_frame, style='Card.TFrame')
            game_frame.grid(row=0, column=i, padx=20, pady=20)
            
            # Add glow effect
            ModernTheme.add_glow_effect(game_frame, games_canvas,
                                      50 + i*420,
                                      200,
                                      350,
                                      300)
            
            # Game content
            icon = ttk.Label(game_frame,
                           text=game['icon'],
                           font=('Segoe UI Emoji', 48),
                           style='Title.TLabel',
                           background=ModernTheme.CARD_BG)
            icon.pack(pady=(30, 0))
            
            title = ttk.Label(game_frame,
                            text=game['title'],
                            style='Subtitle.TLabel',
                            background=ModernTheme.CARD_BG)
            title.pack(pady=(10, 5))
            
            desc = ttk.Label(game_frame,
                           text=game['desc'],
                           style='Sidebar.TLabel',
                           background=ModernTheme.CARD_BG,
                           justify='center',
                           wraplength=300)
            desc.pack(pady=(0, 20))
            
            # Play button with hover effect
            play_btn = ttk.Button(game_frame,
                                text="▶ Play Now",
                                command=lambda s=game['script']: self.run_script(s),
                                style='Sidebar.TButton')
            play_btn.pack(pady=(0, 30))
            
            def on_enter(e, frame=game_frame, btn=play_btn):
                ModernTheme.add_glow_effect(frame, games_canvas,
                                          frame.winfo_x() + frame.master.winfo_x(),
                                          frame.winfo_y() + frame.master.winfo_y(),
                                          frame.winfo_width(),
                                          frame.winfo_height())
                btn.configure(text="🎮 Start Game")
            
            def on_leave(e, frame=game_frame, btn=play_btn):
                ModernTheme.add_glow_effect(frame, games_canvas,
                                          frame.winfo_x() + frame.master.winfo_x(),
                                          frame.winfo_y() + frame.master.winfo_y(),
                                          frame.winfo_width(),
                                          frame.winfo_height())
                btn.configure(text="▶ Play Now")
            
            game_frame.bind('<Enter>', on_enter)
            game_frame.bind('<Leave>', on_leave)
            play_btn.bind('<Enter>', on_enter)
            play_btn.bind('<Leave>', on_leave)
    
    def show_settings(self):
        self.clear_content()
        
        # Create settings container with proper sizing
        settings_canvas = tk.Canvas(self.content_area,
                                  background=ModernTheme.BACKGROUND,
                                  highlightthickness=0,
                                  width=800,
                                  height=600)
        settings_canvas.pack(fill='both', expand=True)
        
        # Create main settings frame
        settings_frame = ttk.Frame(settings_canvas, style='Card.TFrame')
        
        # Position frame using canvas coordinates
        x_pos = 20
        y_pos = 20
        width = 760
        height = 560
        
        # Add glow effect before creating window
        ModernTheme.add_glow_effect(settings_frame, settings_canvas,
                                   x_pos, y_pos, width, height)
        
        # Create canvas window for the frame
        settings_canvas.create_window(x_pos, y_pos,
                                    window=settings_frame,
                                    width=width,
                                    height=height,
                                    anchor='nw')

        # Create notebook with custom style
        style = ttk.Style()
        style.configure('Settings.TNotebook',
                       background=ModernTheme.CARD_BG,
                       borderwidth=0)
        style.configure('Settings.TNotebook.Tab',
                       background=ModernTheme.BACKGROUND,
                       foreground=ModernTheme.TEXT,
                       padding=[20, 10],
                       font=ModernTheme.NORMAL_FONT)
        style.map('Settings.TNotebook.Tab',
                 background=[('selected', ModernTheme.ACCENT)],
                 foreground=[('selected', ModernTheme.BACKGROUND)])
        
        notebook = ttk.Notebook(settings_frame, style='Settings.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Display settings with enhanced layout
        display_frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(display_frame, text="Display")
        
        # Create grid with proper spacing
        display_frame.grid_columnconfigure(1, weight=1)
        for i, (key, value) in enumerate(self.config['display'].items()):
            container = ttk.Frame(display_frame, style='Content.TFrame')
            container.grid(row=i, column=0, columnspan=2, sticky='ew',
                         padx=20, pady=10)
            container.grid_columnconfigure(1, weight=1)
            
            label = ttk.Label(container,
                            text=key.replace('_', ' ').title(),
                            style='Sidebar.TLabel')
            label.grid(row=0, column=0, sticky='w', padx=(0, 20))
            
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                control = ttk.Checkbutton(container,
                                        variable=var,
                                        style='Switch.TCheckbutton')
            else:
                var = tk.DoubleVar(value=float(value))
                control = ttk.Scale(container,
                                  from_=0,
                                  to=100 if 'size' in key else 2000,
                                  variable=var,
                                  orient='horizontal',
                                  style='Slider.Horizontal.TScale')
                
                # Add value label
                value_label = ttk.Label(container,
                                      text=str(int(value)),
                                      style='Sidebar.TLabel')
                value_label.grid(row=0, column=2, padx=(10, 0))
                
                # Update value label on slider change
                def update_label(val, label=value_label):
                    label.configure(text=str(int(float(val))))
                control.configure(command=update_label)
            
            control.grid(row=0, column=1, sticky='ew')
            control.var = var
            control.config_key = key
            
            # Add subtle divider
            if i < len(self.config['display']) - 1:
                divider = ttk.Separator(display_frame,
                                      orient='horizontal',
                                      style='Divider.TSeparator')
                divider.grid(row=i+1, column=0, columnspan=2,
                           sticky='ew', padx=20)
        
        # Colors settings with enhanced color picker
        colors_frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(colors_frame, text="Colors")
        
        for i, (key, value) in enumerate(self.config['colors'].items()):
            container = ttk.Frame(colors_frame, style='Content.TFrame')
            container.grid(row=i, column=0, columnspan=3, sticky='ew',
                         padx=20, pady=15)
            
            label = ttk.Label(container,
                            text=key.replace('_', ' ').title(),
                            style='Sidebar.TLabel')
            label.grid(row=0, column=0, sticky='w', padx=(0, 20))
            
            # Create color preview with rounded corners
            preview_canvas = tk.Canvas(container,
                                     width=40,
                                     height=25,
                                     highlightthickness=0,
                                     background=ModernTheme.CARD_BG)
            preview_canvas.grid(row=0, column=1, padx=(0, 10))
            
            ModernTheme.create_round_rectangle(
                preview_canvas, 0, 0, 40, 25, 5,
                fill='#{:02x}{:02x}{:02x}'.format(*value),
                outline=ModernTheme.ACCENT)
            
            color_btn = ttk.Button(container,
                                 text="Change Color",
                                 command=lambda k=key, c=preview_canvas:
                                     self.choose_color(k, c),
                                 style='Sidebar.TButton')
            color_btn.grid(row=0, column=2)
            
            # Add divider
            if i < len(self.config['colors']) - 1:
                divider = ttk.Separator(colors_frame,
                                      orient='horizontal',
                                      style='Divider.TSeparator')
                divider.grid(row=i+1, column=0, columnspan=3,
                           sticky='ew', padx=20)
        
        # Save button with enhanced styling
        save_container = ttk.Frame(settings_frame, style='Content.TFrame')
        save_container.pack(fill='x', pady=20)
        
        save_btn = ttk.Button(save_container,
                             text="💾 Save Settings",
                             command=self.save_settings,
                             style='Sidebar.TButton')
        save_btn.pack(pady=10)
        
        # Add hover effect to save button
        def on_save_enter(e):
            save_btn.configure(text="💾 Save Changes")
        def on_save_leave(e):
            save_btn.configure(text="💾 Save Settings")
            
        save_btn.bind('<Enter>', on_save_enter)
        save_btn.bind('<Leave>', on_save_leave)

    def save_settings(self):
        # Save with visual feedback
        try:
            self.save_config()
            # Show success message
            msg_frame = ttk.Frame(self.content_area, style='Card.TFrame')
            msg_frame.place(relx=0.5, rely=0.9, anchor='center')
            
            msg = ttk.Label(msg_frame,
                          text="✓ Settings saved successfully!",
                          style='Subtitle.TLabel')
            msg.pack(padx=20, pady=10)
            
            # Remove message after 2 seconds
            self.root.after(2000, msg_frame.destroy)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {str(e)}")

    def choose_color(self, key, preview_canvas):
        current_color = self.config['colors'][key]
        color = colorchooser.askcolor(
            color='#{:02x}{:02x}{:02x}'.format(*current_color),
            title=f"Choose {key.replace('_', ' ').title()} Color"
        )
        if color[0]:
            self.config['colors'][key] = [int(c) for c in color[0]]
            # Update preview
            preview_canvas.delete('all')
            ModernTheme.create_round_rectangle(
                preview_canvas, 0, 0, 40, 25, 5,
                fill='#{:02x}{:02x}{:02x}'.format(*self.config['colors'][key]),
                outline=ModernTheme.ACCENT)
    
    def show_help(self):
        self.clear_content()
        
        # Create main canvas for content and effects
        help_canvas = tk.Canvas(self.content_area,
                              background=ModernTheme.BACKGROUND,
                              highlightthickness=0,
                              width=800,
                              height=600)
        help_canvas.pack(fill='both', expand=True)
        
        # Create help container with glow
        help_frame = ttk.Frame(help_canvas, style='Card.TFrame')
        help_canvas.create_window(20, 20,
                                window=help_frame,
                                width=760,
                                height=560,
                                anchor='nw')
        
        # Add glow effect to main container
        ModernTheme.add_glow_effect(help_frame, help_canvas,
                                   20, 20, 760, 560)
        
        # Title section with proper styling
        header = ttk.Label(help_frame,
                          text="Help & Documentation",
                          style='Title.TLabel',
                          background=ModernTheme.CARD_BG)
        header.pack(pady=(20, 5))
        
        subtitle = ttk.Label(help_frame,
                           text="Learn how to use the Face Tracking Control Center",
                           style='Subtitle.TLabel',
                           background=ModernTheme.CARD_BG)
        subtitle.pack(pady=(0, 20))
        
        # Create scrollable content area
        content_frame = ttk.Frame(help_frame, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Help sections
        sections = [
            {
                'title': '🚀 Getting Started',
                'content': '''• Launch Framework: Start the face tracking system
• Games: Choose from single or multiplayer Pong
• Settings: Customize tracking and display options
• Help: Access this documentation'''
            },
            {
                'title': '🎮 Playing Games',
                'content': '''• Single Player: Control paddle with head movements
• Two Player: Each player uses head tracking
• Stand in front of camera to begin
• Move your head up/down to control paddle'''
            },
            {
                'title': '⚙️ Configuration',
                'content': '''• Display: Adjust window size and UI elements
• Colors: Customize visual appearance
• Tracking: Fine-tune face detection settings
• Save changes before closing'''
            },
            {
                'title': '💡 Tips & Tricks',
                'content': '''• Ensure good lighting for best tracking
• Keep face visible to camera
• Adjust distance for optimal performance
• Use smooth head movements'''
            }
        ]
        
        for i, section in enumerate(sections):
            # Create section card
            section_frame = ttk.Frame(content_frame, style='Card.TFrame')
            section_frame.pack(fill='x', pady=10)
            
            # Section container for proper padding
            inner_frame = ttk.Frame(section_frame, style='Card.TFrame')
            inner_frame.pack(fill='x', padx=20, pady=15)
            
            # Section title
            title = ttk.Label(inner_frame,
                            text=section['title'],
                            style='Subtitle.TLabel',
                            background=ModernTheme.CARD_BG)
            title.pack(anchor='w')
            
            # Content with proper wrapping
            content = ttk.Label(inner_frame,
                              text=section['content'],
                              style='Sidebar.TLabel',
                              background=ModernTheme.CARD_BG,
                              justify='left',
                              wraplength=650)
            content.pack(pady=(10, 0), anchor='w')
            
            # Add divider except for last section
            if i < len(sections) - 1:
                divider = ttk.Separator(content_frame,
                                      orient='horizontal',
                                      style='Divider.TSeparator')
                divider.pack(fill='x', pady=5, padx=40)
        
        # Footer with version
        footer = ttk.Label(help_frame,
                          text="Version 1.0",
                          style='Sidebar.TLabel',
                          background=ModernTheme.CARD_BG)
        footer.pack(side='right', pady=(0, 10), padx=30)
    
    def run_script(self, script_name):
        """Run a Python script"""
        try:
            subprocess.Popen([sys.executable, script_name])
        except Exception as e:
            messagebox.showerror("Error", f"Could not run {script_name}: {str(e)}")

    def run(self):
        """Start the GUI application"""
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernGUI()
    app.run()
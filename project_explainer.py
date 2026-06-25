"""
Project APE - Professional Explainer Video
==========================================

A 2-minute animated explainer video showcasing Project APE's capabilities.

INSTALLATION:
-------------
# Install manim Community Edition
pip install manim

# Or with conda
conda install -c conda-forge manim

# Install required dependencies (macOS)
brew install cairo ffmpeg

# Verify installation
manim --version

USAGE:
------
# Preview in low quality (fast render for testing)
manim project_explainer.py -pql

# Render in high quality (1920x1080, 60fps)
manim project_explainer.py -pqh

# Render specific scene only
manim project_explainer.py Scene1_TitleIntro -pqh

# Output location: media/videos/project_explainer/1080p60/

SCENES:
-------
1. Scene1_TitleIntro (30 seconds) - Title, logo, bullet points
2. Scene2_VisualArchitecture (50 seconds) - Data flow diagram
3. Scene3_WebBrowserDemo (40 seconds) - Web UI simulation

Total runtime: ~2 minutes
"""

from manim import *

# ===========================
# COLOR CONSTANTS - PROJECT APE THEME
# ===========================
BG_DARK = "#0f1419"  # Main background
BG_SECONDARY = "#161b22"  # Card background
TEXT_PRIMARY = "#e6edf3"  # Primary text
TEXT_SECONDARY = "#8b949e"  # Secondary text
ACCENT_RED = "#ee0000"  # Primary accent
PASTEL_BLUE = "#93c5fd"  # Soft blue
PASTEL_GREEN = "#86efac"  # Soft green
PASTEL_RED = "#fca5a5"  # Soft red/pink
PASTEL_ORANGE = "#f0883e"  # Soft orange


# ===========================
# SCENE 1: TITLE & INTRODUCTION
# ===========================
class Scene1_TitleIntro(Scene):
    def construct(self):
        # Set dark background
        self.camera.background_color = BG_DARK

        # === APE LOGO (King Kong) ===
        # Use the actual Project APE King Kong logo
        logo_path = "dashboard/static/kingkong.png"
        king_kong_logo = ImageMobject(logo_path).scale(1.5).shift(UP * 2)

        # Red border around logo
        logo_border = Circle(radius=1.5, color=ACCENT_RED, stroke_width=8).shift(UP * 2)

        # === TITLE TEXT ===
        title = Text("Project APE", font_size=72, weight=BOLD, color=TEXT_PRIMARY)
        title.next_to(king_kong_logo, DOWN, buff=0.5)

        subtitle = Text(
            "AI-Powered Account Planning Engine",
            font_size=32,
            color=TEXT_SECONDARY,
            weight=NORMAL
        ).next_to(title, DOWN, buff=0.3)

        # === BULLET POINTS ===
        bullet_points = VGroup(
            Text("• Automated company research", font_size=28, color=PASTEL_BLUE),
            Text("• AI-generated insights", font_size=28, color=PASTEL_GREEN),
            Text("• Google Drive integration", font_size=28, color=PASTEL_ORANGE),
            Text("• Web-based interface", font_size=28, color=PASTEL_RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        bullet_points.next_to(subtitle, DOWN, buff=0.8)

        # === ANIMATIONS ===
        # Fade in logo with scale effect
        self.play(
            FadeIn(king_kong_logo, scale=0.8),
            Create(logo_border),
            run_time=1.5
        )
        self.wait(0.5)

        # Fade in title and subtitle
        self.play(
            Write(title),
            run_time=1
        )
        self.play(
            FadeIn(subtitle),
            run_time=0.8
        )
        self.wait(1)

        # Fade in bullet points one by one
        for bullet in bullet_points:
            self.play(
                FadeIn(bullet, shift=RIGHT * 0.3),
                run_time=0.8
            )
            self.wait(0.4)

        # Hold final composition
        self.wait(3)

        # Fade out everything
        self.play(
            FadeOut(king_kong_logo),
            FadeOut(logo_border),
            FadeOut(VGroup(title, subtitle, bullet_points)),
            run_time=1
        )


# ===========================
# SCENE 2: VISUAL ARCHITECTURE
# ===========================
class Scene2_VisualArchitecture(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK

        # === TITLE ===
        scene_title = Text("How It Works", font_size=48, weight=BOLD, color=TEXT_PRIMARY)
        scene_title.to_edge(UP, buff=0.5)
        self.play(Write(scene_title), run_time=1)
        self.wait(0.5)

        # === STEP 1: GOOGLE DRIVE FOLDER ===
        drive_icon = self.create_drive_folder()
        drive_icon.shift(LEFT * 5 + UP * 1.5)
        drive_label = Text("Google Drive\nFolder", font_size=20, color=TEXT_SECONDARY)
        drive_label.next_to(drive_icon, DOWN, buff=0.3)

        self.play(FadeIn(drive_icon), FadeIn(drive_label), run_time=1)
        self.wait(0.5)

        # === STEP 2: FILES ===
        files_group = self.create_file_icons()
        files_group.shift(LEFT * 2 + UP * 1.5)

        arrow1 = Arrow(
            drive_icon.get_right(), files_group.get_left(),
            color=PASTEL_BLUE, buff=0.2, stroke_width=6
        )

        self.play(GrowArrow(arrow1), run_time=0.8)
        self.play(FadeIn(files_group, shift=RIGHT * 0.5), run_time=1)
        self.wait(0.5)

        # === STEP 3: NOTEBOOKLM WITH AI SPARKLES ===
        notebooklm_box = self.create_notebooklm_box()
        notebooklm_box.shift(RIGHT * 1.5 + UP * 1.5)

        arrow2 = Arrow(
            files_group.get_right(), notebooklm_box.get_left(),
            color=PASTEL_GREEN, buff=0.2, stroke_width=6
        )

        self.play(GrowArrow(arrow2), run_time=0.8)
        self.play(FadeIn(notebooklm_box, scale=0.9), run_time=1)

        # Add AI sparkles animation
        sparkles = self.create_sparkles(notebooklm_box.get_center())
        self.play(FadeIn(sparkles), run_time=0.5)
        self.play(sparkles.animate.scale(1.5).set_opacity(0), run_time=1)
        self.remove(sparkles)
        self.wait(0.5)

        # === STEP 4: ANALYSIS & RESEARCH ===
        analysis_box = self.create_analysis_box()
        analysis_box.shift(RIGHT * 5 + UP * 1.5)

        arrow3 = Arrow(
            notebooklm_box.get_right(), analysis_box.get_left(),
            color=PASTEL_ORANGE, buff=0.2, stroke_width=6
        )

        self.play(GrowArrow(arrow3), run_time=0.8)
        self.play(FadeIn(analysis_box, shift=RIGHT * 0.5), run_time=1)
        self.wait(0.5)

        # === STEP 5: FINAL ACCOUNT PLAN (PDF) ===
        pdf_icon = self.create_pdf_icon()
        pdf_icon.shift(RIGHT * 1.5 + DOWN * 2)
        pdf_label = Text("Account Plan\n(PDF)", font_size=20, color=TEXT_SECONDARY)
        pdf_label.next_to(pdf_icon, DOWN, buff=0.3)

        arrow4 = Arrow(
            analysis_box.get_bottom(), pdf_icon.get_top(),
            color=PASTEL_RED, buff=0.2, stroke_width=6
        )

        self.play(GrowArrow(arrow4), run_time=0.8)
        self.play(FadeIn(pdf_icon), FadeIn(pdf_label), run_time=1)
        self.wait(1)

        # === PARALLEL PROCESSING VISUALIZATION ===
        # Shrink the main flow
        main_flow = VGroup(
            drive_icon, drive_label, files_group, notebooklm_box,
            analysis_box, pdf_icon, pdf_label, arrow1, arrow2, arrow3, arrow4
        )

        self.play(
            main_flow.animate.scale(0.6).shift(UP * 1.5),
            scene_title.animate.scale(0.8).to_edge(UP, buff=0.3),
            run_time=1.5
        )

        # Show multiple clients processing in parallel
        parallel_label = Text(
            "Multiple Clients in Parallel",
            font_size=36,
            weight=BOLD,
            color=PASTEL_GREEN
        ).shift(DOWN * 1.5)

        client_flows = VGroup()
        for i in range(3):
            flow = self.create_mini_flow()
            flow.shift(DOWN * 2.5 + LEFT * 3 + RIGHT * i * 3)
            client_flows.add(flow)

        self.play(Write(parallel_label), run_time=1)
        self.play(LaggedStart(*[FadeIn(flow) for flow in client_flows], lag_ratio=0.3), run_time=2)
        self.wait(2)

        # Fade out
        self.play(
            FadeOut(VGroup(main_flow, scene_title, parallel_label, client_flows)),
            run_time=1.5
        )

    def create_drive_folder(self):
        """Create a Google Drive folder icon"""
        folder = RoundedRectangle(
            width=1.2, height=1, corner_radius=0.1,
            color=PASTEL_BLUE, fill_opacity=0.3, stroke_width=4
        )
        tab = RoundedRectangle(
            width=0.5, height=0.2, corner_radius=0.05,
            color=PASTEL_BLUE, fill_opacity=0.5, stroke_width=0
        ).next_to(folder, UP, buff=0, aligned_edge=LEFT).shift(RIGHT * 0.1)
        return VGroup(folder, tab)

    def create_file_icons(self):
        """Create a group of file icons"""
        files = VGroup()
        for i in range(3):
            file = RoundedRectangle(
                width=0.5, height=0.7, corner_radius=0.05,
                color=PASTEL_GREEN, fill_opacity=0.3, stroke_width=3
            )
            files.add(file)
        files.arrange(RIGHT, buff=0.2)
        return files

    def create_notebooklm_box(self):
        """Create NotebookLM processing box with AI indicator"""
        box = RoundedRectangle(
            width=2, height=1.5, corner_radius=0.15,
            color=PASTEL_ORANGE, fill_opacity=0.2, stroke_width=5
        )
        text = Text("NotebookLM\nAI Analysis", font_size=20, color=TEXT_PRIMARY)
        text.move_to(box.get_center())
        return VGroup(box, text)

    def create_sparkles(self, position):
        """Create AI sparkle effects"""
        sparkles = VGroup()
        for _ in range(8):
            star = Star(n=4, outer_radius=0.15, color=PASTEL_ORANGE, fill_opacity=0.8)
            star.move_to(position + np.random.randn(3) * 0.5)
            sparkles.add(star)
        return sparkles

    def create_analysis_box(self):
        """Create analysis output box"""
        box = RoundedRectangle(
            width=1.8, height=1.2, corner_radius=0.15,
            color=PASTEL_GREEN, fill_opacity=0.2, stroke_width=5
        )
        text = Text("Insights &\nResearch", font_size=20, color=TEXT_PRIMARY)
        text.move_to(box.get_center())
        return VGroup(box, text)

    def create_pdf_icon(self):
        """Create PDF document icon"""
        doc = RoundedRectangle(
            width=1, height=1.3, corner_radius=0.1,
            color=PASTEL_RED, fill_opacity=0.3, stroke_width=4
        )
        lines = VGroup(*[
            Line(LEFT * 0.3, RIGHT * 0.3, color=TEXT_SECONDARY, stroke_width=2)
            for _ in range(4)
        ]).arrange(DOWN, buff=0.15).move_to(doc.get_center()).shift(DOWN * 0.1)
        return VGroup(doc, lines)

    def create_mini_flow(self):
        """Create miniature flow for parallel processing demo"""
        box1 = RoundedRectangle(width=0.6, height=0.4, corner_radius=0.05,
                                color=PASTEL_BLUE, fill_opacity=0.3, stroke_width=2)
        arrow = Arrow(ORIGIN, RIGHT * 0.5, color=TEXT_SECONDARY, buff=0.05, stroke_width=3)
        box2 = RoundedRectangle(width=0.6, height=0.4, corner_radius=0.05,
                                color=PASTEL_GREEN, fill_opacity=0.3, stroke_width=2)

        flow = VGroup(box1, arrow, box2).arrange(RIGHT, buff=0.1)
        return flow


# ===========================
# SCENE 3: WEB BROWSER DEMO
# ===========================
class Scene3_WebBrowserDemo(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK

        # === BROWSER WINDOW ===
        browser = self.create_browser_window()
        browser.shift(UP * 0.3)

        self.play(FadeIn(browser), run_time=1)
        self.wait(0.5)

        # === SCREEN 1: CONFIGURATION PAGE ===
        config_screen = self.create_config_screen()
        config_screen.move_to(browser[2].get_center())  # Position in content area

        self.play(FadeIn(config_screen), run_time=1)
        self.wait(2)

        # === SCREEN 2: CLICK START WORKFLOW BUTTON ===
        # Highlight the button
        start_button = config_screen[3]  # Get the start button
        highlight = SurroundingRectangle(
            start_button, color=PASTEL_ORANGE, buff=0.15, stroke_width=5
        )

        self.play(Create(highlight), run_time=0.5)
        self.play(FadeOut(highlight), run_time=0.3)

        # Transition to dashboard
        self.play(FadeOut(config_screen), run_time=0.5)
        self.wait(0.3)

        # === SCREEN 3: DASHBOARD WITH PROGRESS BARS ===
        dashboard_screen = self.create_dashboard_screen()
        dashboard_screen.move_to(browser[2].get_center())

        self.play(FadeIn(dashboard_screen), run_time=1)

        # Animate progress bars
        progress_bars = dashboard_screen[1:4]  # Get the progress bar fills
        for bar in progress_bars:
            self.play(bar.animate.stretch_to_fit_width(2.8), run_time=2, rate_func=linear)

        self.wait(1)

        # === SCREEN 4: SUCCESS SCREEN ===
        self.play(FadeOut(dashboard_screen), run_time=0.5)

        success_screen = self.create_success_screen()
        success_screen.move_to(browser[2].get_center())

        self.play(FadeIn(success_screen), run_time=1)
        self.wait(3)

        # === FINAL FADEOUT ===
        self.play(FadeOut(VGroup(browser, success_screen)), run_time=1.5)

        # === ENDING CREDITS ===
        credits = VGroup(
            Text("Project APE", font_size=60, weight=BOLD, color=TEXT_PRIMARY),
            Text("Automate Your Account Planning", font_size=32, color=TEXT_SECONDARY),
            Text("github.com/yourusername/project-ape", font_size=24, color=PASTEL_BLUE),
        ).arrange(DOWN, buff=0.5)

        self.play(FadeIn(credits, shift=UP * 0.5), run_time=1.5)
        self.wait(3)
        self.play(FadeOut(credits), run_time=1)

    def create_browser_window(self):
        """Create a browser window mockup"""
        # Main browser frame
        browser_frame = RoundedRectangle(
            width=12, height=7, corner_radius=0.2,
            color=TEXT_SECONDARY, fill_opacity=0, stroke_width=3
        )

        # Browser header (address bar area)
        header = RoundedRectangle(
            width=12, height=0.8, corner_radius=0.2,
            color=BG_SECONDARY, fill_opacity=1, stroke_width=0
        ).move_to(browser_frame.get_top() + DOWN * 0.4)

        # URL bar
        url_bar = RoundedRectangle(
            width=8, height=0.4, corner_radius=0.1,
            color=BG_DARK, fill_opacity=1, stroke_width=2, stroke_color=TEXT_SECONDARY
        ).move_to(header.get_center())

        url_text = Text(
            "http://localhost:8765",
            font_size=18,
            color=PASTEL_BLUE
        ).move_to(url_bar.get_center())

        # Browser content area
        content_area = Rectangle(
            width=11.6, height=5.8,
            color=BG_DARK, fill_opacity=1, stroke_width=0
        ).next_to(header, DOWN, buff=0.1)

        return VGroup(browser_frame, header, content_area, url_bar, url_text)

    def create_config_screen(self):
        """Create configuration page mockup"""
        # Title
        title = Text("Configure Clients", font_size=32, weight=BOLD, color=TEXT_PRIMARY)
        title.shift(UP * 2)

        # Form fields
        field1 = self.create_form_field("Client Name:", "Acme Corporation")
        field1.shift(UP * 0.8)

        field2 = self.create_form_field("Google Drive Folder:", "https://drive.google.com/...")
        field2.shift(UP * 0.2)

        # Start button
        start_btn = RoundedRectangle(
            width=3, height=0.6, corner_radius=0.1,
            color=ACCENT_RED, fill_opacity=0.8, stroke_width=0
        )
        start_text = Text("🚀 Start Workflow", font_size=24, color=TEXT_PRIMARY, weight=BOLD)
        start_text.move_to(start_btn.get_center())
        start_button = VGroup(start_btn, start_text).shift(DOWN * 1.2)

        return VGroup(title, field1, field2, start_button)

    def create_form_field(self, label, value):
        """Create a form input field"""
        label_text = Text(label, font_size=20, color=TEXT_SECONDARY)
        label_text.shift(LEFT * 3)

        input_box = RoundedRectangle(
            width=5, height=0.5, corner_radius=0.1,
            color=BG_SECONDARY, fill_opacity=1, stroke_width=2, stroke_color=TEXT_SECONDARY
        )
        input_box.next_to(label_text, RIGHT, buff=0.5)

        input_text = Text(value, font_size=18, color=TEXT_PRIMARY)
        input_text.move_to(input_box.get_center())

        return VGroup(label_text, input_box, input_text)

    def create_dashboard_screen(self):
        """Create dashboard with progress bars"""
        title = Text("Workflow Progress", font_size=32, weight=BOLD, color=TEXT_PRIMARY)
        title.shift(UP * 2.3)

        # Create 3 client progress bars
        bars = VGroup()
        client_names = ["Acme Corp", "TechStart Inc", "GlobalBank LLC"]
        colors = [PASTEL_BLUE, PASTEL_GREEN, PASTEL_ORANGE]

        for i, (name, color) in enumerate(zip(client_names, colors)):
            bar_group = self.create_progress_bar(name, color)
            bar_group.shift(UP * (1 - i * 1.2))
            bars.add(bar_group)

        return VGroup(title, *bars)

    def create_progress_bar(self, client_name, color):
        """Create a single progress bar with label"""
        label = Text(client_name, font_size=24, color=TEXT_PRIMARY)
        label.shift(LEFT * 4)

        # Progress bar background
        bar_bg = RoundedRectangle(
            width=6, height=0.4, corner_radius=0.1,
            color=BG_SECONDARY, fill_opacity=1, stroke_width=2, stroke_color=TEXT_SECONDARY
        )
        bar_bg.next_to(label, RIGHT, buff=0.5)

        # Progress bar fill (starts at 0 width)
        bar_fill = RoundedRectangle(
            width=0.1, height=0.36, corner_radius=0.1,
            color=color, fill_opacity=0.8, stroke_width=0
        )
        bar_fill.move_to(bar_bg.get_left() + RIGHT * 0.05, aligned_edge=LEFT)

        return VGroup(label, bar_fill, bar_bg)

    def create_success_screen(self):
        """Create success completion screen"""
        # Success icon (checkmark)
        check_circle = Circle(radius=1.2, color=PASTEL_GREEN, fill_opacity=0.2, stroke_width=6)
        check = Text("✓", font_size=96, color=PASTEL_GREEN, weight=BOLD)
        check.move_to(check_circle.get_center())
        icon = VGroup(check_circle, check).shift(UP * 1)

        # Success message
        message = Text("Workflow Complete!", font_size=40, weight=BOLD, color=TEXT_PRIMARY)
        message.next_to(icon, DOWN, buff=0.8)

        # Quality scores
        scores = VGroup(
            self.create_score_badge("Acme Corp", "8.5/10", PASTEL_BLUE),
            self.create_score_badge("TechStart Inc", "9.2/10", PASTEL_GREEN),
            self.create_score_badge("GlobalBank LLC", "8.8/10", PASTEL_ORANGE),
        ).arrange(RIGHT, buff=0.5)
        scores.next_to(message, DOWN, buff=0.8)

        return VGroup(icon, message, scores)

    def create_score_badge(self, name, score, color):
        """Create a quality score badge"""
        badge = RoundedRectangle(
            width=2.5, height=0.8, corner_radius=0.1,
            color=color, fill_opacity=0.2, stroke_width=3
        )

        name_text = Text(name, font_size=16, color=TEXT_SECONDARY)
        name_text.move_to(badge.get_center() + UP * 0.15)

        score_text = Text(score, font_size=20, color=color, weight=BOLD)
        score_text.move_to(badge.get_center() + DOWN * 0.15)

        return VGroup(badge, name_text, score_text)


# ===========================
# RENDER ALL SCENES TOGETHER
# ===========================
class ProjectExplainerFull(Scene):
    """
    Complete 2-minute explainer video combining all scenes.
    Use this for the final render.
    """
    def construct(self):
        # Scene 1: Title & Introduction
        scene1 = Scene1_TitleIntro()
        scene1.construct()

        # Scene 2: Visual Architecture
        scene2 = Scene2_VisualArchitecture()
        scene2.construct()

        # Scene 3: Web Browser Demo
        scene3 = Scene3_WebBrowserDemo()
        scene3.construct()


# ===========================
# END OF FILE
# ===========================

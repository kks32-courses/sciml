from manim import *

# Use a light theme
config.background_color = WHITE
# Use a consistent color for all text and axes for clarity
config.frame_width = 16
config.frame_height = 9

class DeepONetCalculus(Scene):
    def construct(self):
        # Set default text and math font color to black
        Text.set_default(color=BLACK)
        MathTex.set_default(color=BLACK)

        # --- SCENE 1: THE OPERATOR CHALLENGE ---
        self.next_section("Scene1_OperatorChallenge", skip_animations=False)
        title = Title("DeepONet: Learning a Mathematical Operator")
        self.play(Write(title))

        axis_config = {"color": BLACK, "include_tip": False}
        input_axes = Axes(
            x_range=[-2, 2, 1], y_range=[-4, 4, 2], x_length=5, y_length=4, axis_config=axis_config
        ).to_edge(LEFT, buff=1)
        output_axes = Axes(
            x_range=[-2, 2, 1], y_range=[-2, 6, 2], x_length=5, y_length=4, axis_config=axis_config
        ).to_edge(RIGHT, buff=1)
        
        input_label = input_axes.get_axis_labels(x_label="x", y_label="f(x)")
        output_label = output_axes.get_axis_labels(x_label="x", y_label="G(f)(x)")

        a = ValueTracker(1)
        c = ValueTracker(1)

        input_func = always_redraw(lambda:
            input_axes.plot(lambda x: a.get_value() * x ** 3 + c.get_value() * x, color=BLUE)
        )
        output_func = always_redraw(lambda:
            output_axes.plot(lambda x: 3 * a.get_value() * x ** 2 + c.get_value(), color=ORANGE)
        )
        
        input_formula = MathTex(r"f(x) = ax^3 + cx", color=BLUE).next_to(input_axes, DOWN)
        output_formula = MathTex(r"G(f)(x) = \frac{d}{dx}f(x)", color=ORANGE).next_to(output_axes, DOWN)
        operator_G = MathTex(r"G", font_size=72).move_to(ORIGIN)

        self.play(
            Create(VGroup(input_axes, output_axes, input_label, output_label)),
            Write(VGroup(input_formula, output_formula)),
            FadeIn(operator_G, scale=2)
        )
        self.play(Create(input_func), Create(output_func))
        self.wait()

        self.play(a.animate.set_value(2), c.animate.set_value(-1), run_time=3)
        self.play(a.animate.set_value(0.5), c.animate.set_value(2), run_time=3)
        self.wait()

        # --- SCENE 2: THE DEEPONET ARCHITECTURE ---
        self.next_section("Scene2_Architecture", skip_animations=False)
        self.play(FadeOut(*self.mobjects))
        
        def create_nn(num_inputs, num_hidden, num_outputs, radius=0.15):
            nn = VGroup()
            input_layer = VGroup(*[Circle(radius=radius, color=BLACK, fill_opacity=1) for _ in range(num_inputs)]).arrange(DOWN, buff=0.4)
            hidden_layer = VGroup(*[Circle(radius=radius, color=BLACK, fill_opacity=1) for _ in range(num_hidden)]).arrange(DOWN, buff=0.25)
            output_layer = VGroup(*[Circle(radius=radius, color=BLACK, fill_opacity=1) for _ in range(num_outputs)]).arrange(DOWN, buff=0.4)
            nn.add(input_layer, hidden_layer, output_layer).arrange(RIGHT, buff=1)
            lines = VGroup()
            for i in input_layer:
                for h in hidden_layer: lines.add(Line(i.get_right(), h.get_left(), color=DARK_GRAY, stroke_width=2))
            for h in hidden_layer:
                for o in output_layer: lines.add(Line(h.get_right(), o.get_left(), color=DARK_GRAY, stroke_width=2))
            return VGroup(lines, nn)

        branch_nn = create_nn(3, 5, 2).scale(0.8).shift(UP * 2)
        trunk_nn = create_nn(1, 5, 2).scale(0.8).shift(DOWN * 2)
        branch_label = Text("Branch Net").next_to(branch_nn, UP)
        trunk_label = Text("Trunk Net").next_to(trunk_nn, UP)
        u_input = Text("Input Function f(x)").to_edge(LEFT).shift(UP*2)
        y_input = Text("Output Coordinate y").to_edge(LEFT).shift(DOWN*2)
        arrow_u = Arrow(u_input.get_right(), branch_nn.get_left(), buff=0.2, color=BLACK)
        arrow_y = Arrow(y_input.get_right(), trunk_nn.get_left(), buff=0.2, color=BLACK)
        dot = Dot(point=RIGHT*4, radius=0.1, color=BLACK)
        arrow_b = Arrow(branch_nn.get_right(), dot.get_left(), buff=0.2, color=BLACK)
        arrow_t = Arrow(trunk_nn.get_right(), dot.get_left(), buff=0.2, color=BLACK)
        output_G = MathTex(r"G(f)(y)").next_to(dot, RIGHT, buff=0.3)
        arrow_out = Arrow(dot.get_right(), output_G.get_left(), buff=0.2, color=BLACK)
        
        self.play(
            FadeIn(u_input, arrow_u, branch_nn, branch_label),
            FadeIn(y_input, arrow_y, trunk_nn, trunk_label)
        )
        self.play(FadeIn(dot, arrow_b, arrow_t, output_G, arrow_out))
        self.wait()

        eq1 = MathTex(r"G(f)(y) \approx \text{BranchNet}(f) \cdot \text{TrunkNet}(y)").scale(0.8).to_edge(DOWN)
        self.play(Write(eq1))
        self.wait()
        eq2 = MathTex(r"G(f)(y) \approx \sum_{i=1}^{p} \beta_i h_i(y)").scale(0.8).to_edge(DOWN)
        self.play(Transform(eq1, eq2))
        self.wait()
        
        # --- SCENE 3: The Branch Net ---
        self.next_section("Scene3_BranchNet", skip_animations=False)
        self.play(FadeOut(VGroup(trunk_nn, trunk_label, y_input, arrow_y, arrow_t, dot, output_G, arrow_out, arrow_b)))
        self.play(VGroup(branch_nn, branch_label, u_input, arrow_u, eq1).animate.to_edge(UP))
        
        axes_branch = Axes(x_range=[-2, 2, 1], y_range=[-3, 3, 1], x_length=6, y_length=4, axis_config=axis_config).shift(DOWN*0.5)
        self.play(Create(axes_branch))
        
        sensor_locs = [-1, 0, 1]
        
        def animate_sampling(func_color, u_func, beta_label_tex, beta_pos):
            func_plot = axes_branch.plot(u_func, color=func_color)
            sensors = VGroup(*[Dot(axes_branch.c2p(x, 0), color=BLACK) for x in sensor_locs])
            sensor_lines = VGroup(*[axes_branch.get_vertical_line(axes_branch.c2p(x, u_func(x)), color=DARK_GRAY) for x in sensor_locs])
            self.play(Create(func_plot))
            self.play(Create(sensors), Create(sensor_lines))
            self.play(LaggedStart(*[Indicate(line) for line in sensor_lines]), run_time=2)
            self.play(AnimationGroup(*[ShowPassingFlash(branch_nn.copy().set_color(func_color)) for _ in range(2)], lag_ratio=0.5))
            beta_label = MathTex(beta_label_tex, color=func_color).move_to(beta_pos)
            self.play(Write(beta_label))
            self.wait(0.5)
            self.play(FadeOut(func_plot), FadeOut(sensors), FadeOut(sensor_lines))
            return beta_label
            
        beta1 = animate_sampling(BLUE, lambda x: 1.5 * x**3 - 0.5*x, r"\beta_1", DOWN*0.5 + RIGHT*5)
        beta2 = animate_sampling(RED, lambda x: -1 * x**3 + 2*x, r"\beta_2", DOWN*1.5 + RIGHT*5)
        beta3 = animate_sampling(GREEN, lambda x: 0.5 * x**3 + 1*x, r"\beta_3", DOWN*2.5 + RIGHT*5)
        
        self.play(FadeOut(*self.mobjects))

        u1_mini = axes_branch.plot(lambda x: 1.5 * x**3 - 0.5*x, color=BLUE).scale(0.3)
        u2_mini = axes_branch.plot(lambda x: -1 * x**3 + 2*x, color=RED).scale(0.3)
        u3_mini = axes_branch.plot(lambda x: 0.5 * x**3 + 1*x, color=GREEN).scale(0.3)
        mini_funcs = VGroup(u1_mini, u2_mini, u3_mini).arrange(DOWN, buff=0.5).move_to(LEFT*5)
        beta_labels_group = VGroup(beta1, beta2, beta3).arrange(DOWN, buff=0.8).move_to(RIGHT*5)
        arrow1 = Arrow(mini_funcs[0].get_right(), beta_labels_group[0].get_left(), buff=0.3, color=BLACK)
        arrow2 = Arrow(mini_funcs[1].get_right(), beta_labels_group[1].get_left(), buff=0.3, color=BLACK)
        arrow3 = Arrow(mini_funcs[2].get_right(), beta_labels_group[2].get_left(), buff=0.3, color=BLACK)
        
        self.play(LaggedStart(FadeIn(mini_funcs), FadeIn(beta_labels_group)))
        self.play(GrowArrow(arrow1), GrowArrow(arrow2), GrowArrow(arrow3))
        from_text = Text("From a Function Space").scale(0.7).next_to(mini_funcs, UP)
        to_text = Text("...to a Coefficient Space").scale(0.7).next_to(beta_labels_group, UP)
        self.play(Write(from_text), Write(to_text))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- SCENE 4: The Trunk Net ---
        self.next_section("Scene4_TrunkNet", skip_animations=False)
        
        basis_axes = Axes(x_range=[-1.5, 1.5, 1], y_range=[0, 3, 1], x_length=6, y_length=4, axis_config=axis_config).shift(RIGHT*2)
        basis_label = Text("Basis Functions").scale(0.7).next_to(basis_axes, UP)
        y_tracker = ValueTracker(-1.5)
        y_dot = Dot(color=BLACK).add_updater(lambda d: d.move_to(basis_axes.c2p(y_tracker.get_value(), 0)))
        
        h1_initial = basis_axes.plot(lambda y: np.sin(y*PI) + 1.5, color=PURPLE)
        h2_initial = basis_axes.plot(lambda y: np.cos(y*2*PI) + 1, color=TEAL)
        
        self.play(Create(basis_axes), Write(basis_label))
        training_text = Text("Training...").scale(0.6).to_edge(DOWN, buff=1)
        self.play(Write(training_text))
        self.play(Create(VGroup(h1_initial, h2_initial)))
        self.play(FadeIn(y_dot))
        self.play(y_tracker.animate.set_value(1.5), rate_func=linear, run_time=3)
        
        h1_final = basis_axes.plot(lambda y: 1, color=PURPLE)
        h2_final = basis_axes.plot(lambda y: y**2, color=TEAL)
        h1_label = MathTex("h_1(y)", color=PURPLE).next_to(h1_final, RIGHT)
        h2_label = MathTex("h_2(y)", color=TEAL).next_to(h2_final, UR, buff=0.1)

        self.play(Transform(h1_initial, h1_final), Transform(h2_initial, h2_final))
        self.play(Write(h1_label), Write(h2_label))
        self.play(FadeOut(training_text), FadeOut(y_dot))
        self.wait(2)
        
        # --- SCENE 5: Combination and Prediction ---
        self.next_section("Scene5_Combination", skip_animations=False)
        self.play(FadeOut(*self.mobjects))
        
        full_diagram = VGroup(create_nn(3,5,2), create_nn(1,5,2)).arrange(DOWN, buff=1.5).scale(0.8)
        self.play(FadeIn(full_diagram))
        
        output_axes_final = Axes(x_range=[-2, 2, 1], y_range=[-2, 8, 2], x_length=6, y_length=4, axis_config=axis_config).shift(DOWN*0.5)
        output_axes_label = Text("Final Output G(f)(y)").scale(0.7).next_to(output_axes_final, UP)
        self.play(Transform(full_diagram, VGroup(output_axes_final, output_axes_label)))

        beta_1_true, beta_2_true = -0.5, 4.5
        
        solid_line = output_axes_final.plot(lambda x: beta_2_true * x**2 + beta_1_true, color=BLUE)
        true_derivative = DashedVMobject(solid_line, num_dashes=30, color=BLUE)
        
        eq_sum = MathTex(r"G(u_1)(y) = \beta_1 h_1(y) + \beta_2 h_2(y)").to_edge(UP)
        
        wrong_beta1 = ValueTracker(2.0)
        wrong_beta2 = ValueTracker(1.0)
        
        pred = always_redraw(
            lambda: output_axes_final.plot(
                lambda y: wrong_beta1.get_value() * 1 + wrong_beta2.get_value() * y**2, color=RED
            )
        )
        
        loss_text = Text("Loss:", color=RED).to_edge(DOWN)
        loss_val = DecimalNumber(15.73, color=RED, num_decimal_places=2).next_to(loss_text, RIGHT)
        loss_val.add_updater(lambda d: d.set_value( (wrong_beta1.get_value() - beta_1_true)**2 + (wrong_beta2.get_value() - beta_2_true)**2 ))
        
        self.play(FadeIn(eq_sum))
        self.play(Create(pred), Write(loss_text), Write(loss_val))
        self.play(Create(true_derivative))
        self.wait()
        
        self.play(
            wrong_beta1.animate.set_value(beta_1_true), 
            wrong_beta2.animate.set_value(beta_2_true),
            run_time=3
        )
        self.wait(0.5)
        pred.clear_updaters()
        loss_val.clear_updaters()
        self.play(loss_val.animate.set_value(0.01))
        self.play(Circumscribe(pred, color=GREEN))
        self.wait(2)
        
        # --- SCENE 6: GENERALIZATION ---
        self.next_section("Scene6_Generalization", skip_animations=False)
        self.play(FadeOut(*self.mobjects))
        
        final_title = Title("The Generalization Payoff")
        self.play(Write(final_title))
        
        input_axes = Axes(x_range=[-2, 2, 1], y_range=[-4, 4, 2], x_length=5, y_length=4, axis_config=axis_config).to_edge(LEFT, buff=1)
        output_axes = Axes(x_range=[-2, 2, 1], y_range=[-2, 8, 2], x_length=5, y_length=4, axis_config=axis_config).to_edge(RIGHT, buff=1)
        
        u_new = input_axes.plot(lambda x: -1*x**3 + 2.5*x, color=GREEN)
        
        G_u_new_solid = output_axes.plot(lambda x: -3*x**2 + 2.5, color=GREEN)
        G_u_new_true = DashedVMobject(G_u_new_solid, num_dashes=30, color=GREEN)
        G_u_new_pred = output_axes.plot(lambda x: -3*x**2 + 2.5, color=RED)

        self.play(Create(VGroup(input_axes, output_axes)), Write(u_new))
        self.wait(1)
        
        arrow_predict = Arrow(input_axes.get_right(), output_axes.get_left(), buff=0.5, color=BLACK)
        self.play(GrowArrow(arrow_predict))
        self.play(Create(G_u_new_pred))
        self.wait(0.5)
        self.play(FadeIn(G_u_new_true, run_time=0.5))
        self.play(Circumscribe(G_u_new_pred, color=GOLD), Circumscribe(u_new, color=GOLD))
        self.wait(3)
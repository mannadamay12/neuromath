from manim import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.rotate(PI / 4)
        self.play(Create(square))
        self.play(Transform(square, circle))
        self.wait()
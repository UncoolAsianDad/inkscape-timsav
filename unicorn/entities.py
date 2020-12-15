import math


class Entity:
	def get_gcode(self, context):
		# raise NotImplementedError()
		return "NIE"


class Line(Entity):
	def __init__(self):
		self.start = None
		self.end = None

	def __str__(self):
		return "Line from [%.2f, %.2f] to [%.2f, %.2f]" % (self.start[0], self.start[1], self.end[0], self.end[1])

	def get_gcode(self, context):
		"""Emit gcode for drawing line"""
		context.codes.append("(" + str(self) + ")")
		context.go_to_point(self.start[0], self.start[1])
		context.draw_to_point(self.end[0], self.end[1])
		context.codes.append("")


class Circle(Entity):
	def __init__(self):
		self.center = None
		self.radius = None
		self.cutStyle = None

	def __str__(self):
		return "Circle at [%.2f,%.2f], radius %.2f" % (self.center[0], self.center[1], self.radius)

	def get_gcode(self, context):
		"""Emit gcode for drawing arc"""
		start = (self.center[0] - self.radius, self.center[1])
		arc_code = "G3 I%.2f J0 F%.2f" % (self.radius, context.xy_feedrate)

		context.codes.append("(" + str(self) + ")")
		context.go_to_point(start[0], start[1])
		context.start(self.cutStyle)
		context.codes.append(arc_code)
		context.stop()
		context.codes.append("")


class Arc(Entity):
	def __init__(self):
		self.center = None
		self.radius = None
		self.start_angle = None
		self.end_angle = None
		self.cut_style = None

	def __str__(self):
		return "Arc at [%.2f, %.2f], radius %.2f, from %.2f to %.2f" % (
			self.center[0], self.center[1], self.radius, self.start_angle, self.end_angle)

	def find_point(self, proportion):
		"""Find point at the given proportion along the arc."""
		delta = self.end_angle - self.start_angle
		angle = self.start_angle + delta * proportion

		return self.center[0] + self.radius * math.cos(angle), self.center[1] + self.radius * math.sin(angle)

	def get_gcode(self, context):
		"""Emit gcode for drawing arc"""
		start = self.find_point(0)
		end = self.find_point(1)
		delta = self.end_angle - self.start_angle

		if delta < 0:
			arc_code = "G3"
		else:
			arc_code = "G3"
		arc_code = arc_code + " X%.2f Y%.2f I%.2f J%.2f F%.2f" % (
			end[0], end[1], self.center[0] - start[0], self.center[1] - start[1], context.xy_feedrate)

		context.codes.append("(" + str(self) + ")")
		context.go_to_point(start[0], start[1])
		context.last = end
		context.start(self.cut_style)
		context.codes.append(arc_code)
		context.stop()
		context.codes.append("")


class PolyLine(Entity):
	def __init__(self):
		self.segments = None
		self.cut_style = None

	def __str__(self):
		return "Polyline consisting of %d segments." % len(self.segments)

	def get_gcode(self, context):
		"""Emit gcode for drawing polyline"""
		if hasattr(self, 'segments'):
			for points in self.segments:
				start = points[0]

				context.codes.append("(" + str(self) + ")")
				context.go_to_point(start[0], start[1])
				context.start(self.cut_style)
				for point in points[1:]:
					context.draw_to_point(point[0], point[1])
					context.last = point
				context.stop()
				context.codes.append("")

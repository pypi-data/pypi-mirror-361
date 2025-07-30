union() {
	for(scad_for_index = [0:1:7]) {
		translate(v = [0, 0, (scad_for_index * 2)]) {
			cube(size = 1);
		}

	}
	if(($t < 0.5)) {
		translate(v = [-5, 0, 0]) {
			cube(size = 2);
		}

	} else {
		color(alpha = 1.0, c = "red") {
			translate(v = [-5, 0, 0]) {
				cube(size = 2);
			}
		}

	}
}

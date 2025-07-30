number_of_cubes = 7; //[]
alt_color = "red"; //[red, blue, green]

union() {
	for(scad_for_index = [0:1:number_of_cubes]) {
		translate(v = [0, 0, (scad_for_index * 2)]) {
			union() {
				if(((scad_for_index % 2) == 0)) {
					cube();

				} else {
					color(alpha = 1.0, c = alt_color) {
						cube();
					}

				}
			}
		}

	}
}

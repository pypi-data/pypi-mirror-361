#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform int n;

out vec3 fragColor;

int quot(int x, int y)
{
	return int(floor(x/y));
}

void main()
{
	int x = int(fragCoord.x);
	int y = int(fragCoord.y);
	vec3 c;
	c.r = mod(x,n)/(n-1);
	c.g = mod(y,n)/(n-1);
	int slice_x = quot(x,n);
	int slice_y = quot(y,n);
	c.b = (slice_y*sqrt(n)+slice_x)/n;
	fragColor = vec3(c);
}
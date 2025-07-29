#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform vec3 iResolution;
uniform int n;
uniform float t;

out vec3 fragColor;

vec3 lerp(
	float x,
	vec3 f0,vec3 f1)
{
	vec3 fx = (1-x)*f0+x*f1;
	return fx;
}

vec3 bilerp(
	float x,float y,
	vec3 f00,vec3 f10,vec3 f01,vec3 f11)
{
	vec3 fx0 = lerp(x,f00,f10);
	vec3 fx1 = lerp(x,f01,f11);
	vec3 fxy = lerp(y,fx0,fx1);
	return fxy;
}

vec3 trilerp(
	float x, float y, float z,
	vec3 f000, vec3 f100, vec3 f010, vec3 f110,
	vec3 f001, vec3 f101, vec3 f011, vec3 f111)
{
	vec3 fxy0 = bilerp(x,y,f000,f100,f010,f110);
	vec3 fxy1 = bilerp(x,y,f001,f101,f011,f111);
	vec3 fxyz = lerp(z,fxy0,fxy1);
	return fxyz;
}

int quot(int x, int y)
{
	return int(floor(x/y));
}

int rem(int x, int y)
{
	return x % y;
}

vec3 lookup(int x,int y)
{
	vec2 uv = (vec2(x,y)+vec2(0.5,0.5))/(n*sqrt(n));
	return texture(iChannel1,uv).rgb;
}

void main()
{
	vec2 uv = fragCoord/iResolution.xy;
	vec4 c_in = texture(iChannel0,uv);
	int slices_per_row = int(sqrt(n));
	int front_i =
		int(min(floor(c_in.b*n),n-1));
	int front_x =
		rem(front_i,slices_per_row)*n;
	int front_y =
		quot(front_i,slices_per_row)*n;
	int back_i =
		int(min(ceil(c_in.b*n),n-1));
	int back_x =
		rem(back_i,slices_per_row)*n;
	int back_y =
		quot(back_i,slices_per_row)*n;
	int left = int(min(floor(c_in.r*n),n-1));
	int right = int(min(ceil(c_in.r*n),n-1));
	int top = int(min(floor(c_in.g*n),n-1));
	int bot = int(min(ceil(c_in.g*n),n-1));
	int x000,x100,x010,x110,x001,x101,x011,x111;
	int y000,y100,y010,y110,y001,y101,y011,y111;
	x000 = x010 = front_x+left;
	x100 = x110 = front_x+right;
	y000 = y100 = front_y+top;
	y010 = y110 = front_y+bot;
	x001 = x011 = back_x+left;
	x101 = x111 = back_x+right;
	y001 = y101 = back_y+top;
	y011 = y111 = back_y+bot;
	vec3 c000 = lookup(x000,y000);
	vec3 c100 = lookup(x100,y100);
	vec3 c010 = lookup(x010,y010);
	vec3 c110 = lookup(x110,y110);
	vec3 c001 = lookup(x001,y001);
	vec3 c101 = lookup(x101,y101);
	vec3 c011 = lookup(x011,y011);
	vec3 c111 = lookup(x111,y111);
	vec3 c_out = trilerp(c_in.r,c_in.g,c_in.b,
		c000,c100,c010,c110,c001,c101,c011,c111);
	fragColor = mix(c_in.rgb,c_out.rgb,t);
}
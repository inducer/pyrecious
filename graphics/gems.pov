#include "colors.inc"

camera 
{
  location -z*3
  look_at z
  up y
  right x
}

light_source 
{
  <20,20,9>
  color White
}
light_source 
{
  <20,20,6>
  color White
}
light_source 
{
  <5,2,-10>
  color White
}
light_source 
{
  <-10,20,-20>
  color White
}

#macro O_GemCylinder1(side_count)
  intersection 
  {
    #local rot_angle = 0;
    #while ( rot_angle < 360 )
      plane 
      { 
	x,1 
	rotate z*rot_angle
      }
      #local rot_angle = rot_angle + (360/side_count);
    #end
  }
#end

#macro O_Gem1( side_count, inner_side_count, x_rotation )
  intersection 
  {
    #local rot_angle = 0;
    #while ( rot_angle < 360 )
      object
      { 
	O_GemCylinder1( inner_side_count )
	rotate x*x_rotation
	rotate z*rot_angle
      }
      #local rot_angle = rot_angle + (360 / side_count );
    #end
  }
#end

object 
{
  /* known good values:
    8, 8, 90
    6, 6, 90
  */
  O_Gem1( SIDE_COUNT, INNER_SIDE_COUNT, INNER_ROTATION )
  rotate y*ROTATION
  scale SCALE_FACTOR

  texture 
  {
    pigment 
    {
      color COLOR filter 0.85
    }

    finish 
    {
      ambient rgb <GEM_AMBIENT,GEM_AMBIENT,GEM_AMBIENT>
      diffuse 0.85

      phong 0.3
      phong_size 40
      
      brilliance 0.9
    }
  }
  interior 
  {
    fade_distance 20
    fade_power 1
  }
}


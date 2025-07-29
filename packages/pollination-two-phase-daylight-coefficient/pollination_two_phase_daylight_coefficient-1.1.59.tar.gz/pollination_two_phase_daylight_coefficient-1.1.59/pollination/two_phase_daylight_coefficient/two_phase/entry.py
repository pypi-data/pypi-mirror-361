from pollination_dsl.dag import Inputs, DAG, task
from pollination_dsl.dag.inputs import ItemType
from dataclasses import dataclass
from pollination.honeybee_radiance_postprocess.grid import MergeFolderData

from ._raytracing import TwoPhaseRayTracing


@dataclass
class TwoPhaseSimulation(DAG):
    """Two phase entry point.

    This two phase workflow also includes the extra phase for accurately calculating the
    direct sunlight.
    """

    # inputs
    identifier = Inputs.str(
        description='Identifier for this two-phase study. This value is usually the '
        'identifier of the aperture group or is set to __static__ for the static '
        'apertures in the model.', default='__static__'
    )

    light_path = Inputs.str(
        description='Identifier for the light path of this two-phase study. This value '
        'is the identifier of the aperture group or is set to __static___ for the '
        'static apertures in the model.', default='__static__'
    )

    radiance_parameters = Inputs.str(
        description='The radiance parameters for ray tracing.',
        default='-ab 2 -ad 5000 -lw 2e-05'
    )

    sensor_grids_info = Inputs.list(
        description='A list with sensor grids information.',
        items_type=ItemType.JSONObject
    )

    sensor_grids_folder = Inputs.folder(
        description='Corresponding sensor grid folder to sensor grids info.'
    )

    octree_file = Inputs.file(
        description='Octree that describes the scene for indirect studies. This octree '
        'includes all the scene with default modifiers except for the aperture groups '
        'other the one that is the source for this calculation will be blacked out.',
        extensions=['oct']
    )

    octree_file_direct = Inputs.file(
        description='Octree that describes the scene for direct studies. This octree '
        'is similar to the octree for indirect studies with the difference that the '
        'matrials for the scene are set to black.',
        extensions=['oct']
    )

    octree_file_with_suns = Inputs.file(
        description='A blacked out octree that includes the sunpath. This octree is '
        'used for calculating the contribution from direct sunlight.',
        extensions=['oct']
    )

    sky_dome = Inputs.file(
        description='A sky dome for daylight coefficient studies.'
    )

    total_sky = Inputs.file(
        description='Sky matrix with both sun and sky components.'
    )

    direct_sky = Inputs.file(
        description='Sky matrix with sun only.'
    )

    sun_modifiers = Inputs.file(
        description='The list of sun modifiers that are included in octree_direct_sun.'
    )

    bsdf_folder = Inputs.folder(
        description='The folder from Radiance model folder that includes the BSDF files.'
        'You only need to include the in-scene BSDFs for the two phase calculation.',
        optional=True
    )

    results_folder = Inputs.str(
        description='An optional string to define the folder that the outputs should be '
        'copied to. You can use this input to copy the final results to a folder other '
        'then the subfolder for this DAG', default='results'
    )

    dtype = Inputs.str(
        description='Switch between float32 and float 16 data type. Default '
        'is float32.',
        spec={'type': 'string', 'enum': ['float32', 'float16']},
        default='float32'
    )

    @task(
        template=TwoPhaseRayTracing,
        loop=sensor_grids_info,
        # create a subfolder for each grid
        sub_folder='initial_results/{{item.full_id}}',
        # sensor_grid sub_path
        sub_paths={'sensor_grid': '{{item.full_id}}.pts'}
    )
    def two_phase_raytracing(
        self,
        radiance_parameters=radiance_parameters,
        octree_file=octree_file,
        octree_file_direct=octree_file_direct,
        octree_file_with_suns=octree_file_with_suns,
        grid_name='{{item.full_id}}',
        sensor_grid=sensor_grids_folder,
        sensor_count='{{item.count}}',
        sky_matrix=total_sky,
        sky_matrix_direct=direct_sky,
        sky_dome=sky_dome,
        sun_modifiers=sun_modifiers,
        bsdfs=bsdf_folder,
        dtype=dtype
    ):
        pass

    @task(
        template=MergeFolderData,
        needs=[two_phase_raytracing],
        sub_paths={
            'dist_info': '_redist_info.json'
        }
    )
    def restructure_total_results(
        self, identifier=identifier, light_path=light_path,
        input_folder='initial_results/final/total',
        extension='ill', dist_info=sensor_grids_folder,
        results_folder=results_folder
    ):
        return [
            {
                'from': MergeFolderData()._outputs.output_folder,
                'to': '{{self.results_folder}}/{{self.light_path}}/{{self.identifier}}/total'
            }
        ]

    @task(
        template=MergeFolderData,
        needs=[two_phase_raytracing],
        sub_paths={
            'dist_info': '_redist_info.json'
        }
    )
    def restructure_direct_sunlight_results(
        self, identifier=identifier, light_path=light_path,
        input_folder='initial_results/final/direct',
        extension='ill', dist_info=sensor_grids_folder,
        results_folder=results_folder
    ):
        return [
            {
                'from': MergeFolderData()._outputs.output_folder,
                'to': '{{self.results_folder}}/{{self.light_path}}/{{self.identifier}}/direct'
            }
        ]

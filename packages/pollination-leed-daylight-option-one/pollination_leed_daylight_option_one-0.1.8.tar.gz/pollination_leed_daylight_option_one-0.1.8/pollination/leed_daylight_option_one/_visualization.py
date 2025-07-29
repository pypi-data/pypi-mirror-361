from dataclasses import dataclass
from pollination_dsl.dag import Inputs, GroupedDAG, task, Outputs
from pollination.honeybee_display.translate import ModelToVis
from pollination.path.copy import CopyFolder
from pollination.honeybee_radiance_postprocess.leed import DaylightOptionOneVisMetadata


@dataclass
class DaylightOptionOneVisualization(GroupedDAG):
    """Create visualization."""

    # inputs
    model = Inputs.file(
        description='Input Honeybee model.',
        extensions=['json', 'hbjson', 'pkl', 'hbpkl', 'zip']
    )

    pass_fail = Inputs.folder(
        description='Pass/fail results.',
        path='results'
    )

    @task(template=CopyFolder)
    def copy_pass_fail(self, src=pass_fail):
        return [
            {
                'from': CopyFolder()._outputs.dst,
                'to': 'visualization'
            }
        ]

    @task(
        template=DaylightOptionOneVisMetadata,
    )
    def create_vis_metadata(self):
        return [
            {
                'from': DaylightOptionOneVisMetadata()._outputs.vis_metadata_folder,
                'to': 'visualization'
            }
        ]

    @task(
        template=ModelToVis,
        needs=[copy_pass_fail, create_vis_metadata]
    )
    def create_vsf(
        self, model=model, grid_data='visualization',
        active_grid_data='DA', output_format='vsf'
    ):
        return [
            {
                'from': ModelToVis()._outputs.output_file,
                'to': 'visualization.vsf'
            }
        ]

    visualization = Outputs.file(
        source='visualization.vsf',
        description='Visualization in VisualizationSet format.'
    )

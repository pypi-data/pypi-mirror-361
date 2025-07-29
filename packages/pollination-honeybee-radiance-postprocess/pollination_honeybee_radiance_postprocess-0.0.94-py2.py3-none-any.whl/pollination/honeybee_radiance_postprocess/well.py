from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class WellAnnualDaylight(Function):
    """Calculate credits for WELL L06 and L01."""

    folder = Inputs.folder(
        description='This folder is an output folder of annual daylight recipe. Folder '
        'should include grids_info.json and sun-up-hours.txt. The command uses the list '
        'in grids_info.json to find the result files for each sensor grid.',
        path='results'
    )

    grid_filter = Inputs.str(
        description='Text for a grid identifier or a pattern to filter the sensor grids '
        'of the model that are simulated. For instance, first_floor_* will simulate '
        'only the sensor grids that have an identifier that starts with '
        'first_floor_. By default, all grids in the model will be simulated.',
        default='*'
    )

    model = Inputs.file(
        description='Path to HBJSON file. The purpose of the model in this function is '
        'to use the mesh area of the sensor grids to calculate area-weighted metrics. '
        'In case no model is provided or the sensor grids in the model do not have any '
        'mesh area, it will be assumed that all sensor points cover the same area.',
        path='model.hbjson', optional=True
    )

    daylight_hours = Inputs.file(
        description='Path to an annual schedule file. Values should be 0-1 separated '
        'by new line. This should be a daylight hours schedule according to EN 17037.',
        path='daylight_hours.txt'
    )

    @command
    def well_annual_daylight(self):
        return 'honeybee-radiance-postprocess post-process well well-annual-daylight ' \
            'results daylight_hours.txt --grids-filter " {{self.grid_filter}} " ' \
            '--sub-folder well_summary'

    # outputs
    well_summary_folder = Outputs.folder(
        description='WELL summary folder.',
        path='well_summary'
    )

    ies_lm_folder = Outputs.folder(
        description='IES LM summary folder.',
        path='well_summary/ies_lm'
    )

    en17037_folder = Outputs.folder(
        description='EN 17037 summary folder.',
        path='well_summary/en17037'
    )

    l01_well_summary = Outputs.file(
        description='L01 WELL summary.',
        path='well_summary/l01_well_summary.json'
    )

    l01_ies_folder = Outputs.folder(
        description='L01 IES LM folder.',
        path='well_summary/ies_lm/l01_ies_lm_summary'
    )

    l06_well_summary = Outputs.file(
        description='L06 WELL summary.',
        path='well_summary/l06_well_summary.json'
    )


    l06_ies_folder = Outputs.folder(
        description='L06 IES LM folder.',
        path='well_summary/ies_lm/l06_ies_lm_summary'
    )


@dataclass
class WellDaylightVisMetadata(Function):
    """Create visualization metadata files for WELL Daylight."""

    output_folder = Inputs.str(
        description='Name of the output folder.', default='visualization',
        path='visualization'
    )

    @command
    def create_well_daylight_vis_data(self):
        return 'honeybee-radiance-postprocess post-process well well-daylight-vis-metadata ' \
            '--output-folder "{{self.output_folder}}"'

    # outputs
    vis_metadata_folder = Outputs.folder(
        description='Output folder with visualization metadata files.',
        path='visualization'
    )

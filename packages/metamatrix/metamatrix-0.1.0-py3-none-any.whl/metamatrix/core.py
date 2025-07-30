import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_hex, TwoSlopeNorm
from svg import SVG, Rect, Title, Text, G

# - A-matrix = main matrix
# - B-matrix = matrix to the right
# - C-matrix = matrix at the bottom

class MetaMatrix():
    def __init__(self, df_A, df_B, df_C, **kwargs):
        defaults = {
            'features': {'row': {}, 'column': {}},
            'padding_top': 120,
            'padding_left': 80,
            'cell_width': 5,
            'cell_height': 15,
            'row_metadata_cell_width': 20,
            'column_metadata_cell_height': 20,
            'column_labels': False,
            'row_labels': True,
            'column_order': '',
            'row_order': ''
        }
        self.df_A = df_A
        self.df_B = df_B
        self.df_C = df_C

        for key, value in {**defaults, **kwargs}.items():
            setattr(self, key, value)

        self.df_B_dict = self.df_B.to_dict(orient="index")
        self.df_C_dict = self.df_C.to_dict(orient="index")

        if self.column_order != '':
            _sorted_columns = sorted(
                self.df_A.columns,
                key=lambda _col: self.df_C_dict.get(_col, {}).get(self.column_order, '')
            )
            self.df_A = self.df_A[_sorted_columns]
        if self.row_order != '':
            _sorted_index = sorted(
                self.df_A.index,
                key=lambda _idx: self.df_B_dict.get(_idx, {}).get(self.row_order, '')
            )
            self.df_A = self.df_A.loc[_sorted_index]

        self.column_features = list(self.features.get('column', {}).keys())
        self.row_features = list(self.features.get('row', {}).keys())

        self.scales = {'values': self.make_numeric_colour_scale(0,np.max(self.df_A.values),"white","blue")}

        self.create_scales()

    ### Helper functions to create colour scales
    def make_numeric_colour_scale(self, domain_min, domain_max, colour_start, colour_end):
        cmap = LinearSegmentedColormap.from_list("custom", [colour_start, colour_end])
        norm = Normalize(vmin=domain_min, vmax=domain_max)
        return lambda x: to_hex(cmap(norm(x)))  # returns hex string

    def make_categorical_colour_scale(self, categories, cmap_name='Set2'):
        cmap = plt.get_cmap(cmap_name)
        colour_dict = {cat: to_hex(cmap(i)) for i, cat in enumerate(categories)}
        return lambda x: colour_dict[x]

    def make_diverging_colour_scale(self, data_min, data_max, colour_neg='blue', colour_pos='red'):
        abs_max = max(abs(data_min), abs(data_max))
        norm = TwoSlopeNorm(vmin=-abs_max, vcenter=0, vmax=abs_max)
        cmap = LinearSegmentedColormap.from_list("diverging", [colour_neg, 'white', colour_pos])
        return lambda x: to_hex(cmap(norm(x)))

    ### Create colour scales for each metadata
    def create_scales(self):
        # Process row metadata: df_B
        for _feature in self.column_features:
            scale_type = self.features['column'].get(_feature)

            if scale_type == 'categorical':
                categories = self.df_C[_feature].dropna().unique()
                self.scales[_feature] = self.make_categorical_colour_scale(categories)

            elif scale_type == 'numeric':
                values = self.df_C[_feature].dropna().astype(float)
                vmin, vmax = (values.min(), values.max())
                self.scales[_feature] = self.make_numeric_colour_scale(vmin, vmax, 'blue', 'red')

        # Process column metadata: df_C
        for _feature in self.row_features:
            scale_type = self.features['row'].get(_feature)

            if scale_type == 'categorical':
                categories = self.df_B[_feature].dropna().unique()
                self.scales[_feature] = self.make_categorical_colour_scale(categories)

            elif scale_type == 'numeric':
                values = self.df_B[_feature].dropna().astype(float)
                vmin, vmax = (values.min(), values.max())
                self.scales[_feature] = self.make_numeric_colour_scale(vmin, vmax, 'blue', 'red')

    ### Create the complete SVG group
    def to_group(self):        
        ####################################################
        ## Data: df_A
        ####################################################
        _data_cells = []

        # Column labels at the top
        if self.column_labels:
            for _idx, _col in enumerate(self.df_A.columns):
                _data_cells.append(Text(
                        x=0, y=0,
                        text=_col,
                        text_anchor="middle",
                        font_size=12,
                        style="dominant-baseline: middle; text-anchor: start;",
                        transform=f"translate({_idx*self.cell_width + self.cell_width/2},-3) rotate(270)"
                    ))

        # For each row
        for _idx_y, (_label, _row) in enumerate(self.df_A.iterrows()):
            # Row label at the left
            if self.row_labels:
                _data_cells.append(Text(
                    x=0, y=0,
                    text=_label,
                    text_anchor="middle",
                    font_size=12,
                    style="dominant-baseline: middle; text-anchor: end;",
                    transform=f"translate(-3,{_idx_y*self.cell_height+self.cell_height/2})"
                ))
            for _idx_x, _col in enumerate(self.df_A):
                _value = _row[_col]
                _data_cells.append(Rect(
                    x=_idx_x*self.cell_width,
                    y=_idx_y*self.cell_height,
                    width=self.cell_width-1,
                    height=self.cell_height-1,
                    fill=self.scales['values'](_value),
                    elements=[Title(elements=f"{_label} {_col} {_value}")]
                ))
        _matrix_A_group = G(
            elements=[_data_cells]
        )

        ####################################################
        ## Row metadata: df_B
        ####################################################
        _row_groups = []
        # Print the feature labels at the bottom
        for _idx, _feature in enumerate(self.row_features):
            _row_groups.append(Text(
                    x=0, y=0,
                    text=_feature,
                    text_anchor="middle",
                    font_size=12,
                    style="dominant-baseline: middle; text-anchor: start;",
                    transform=f"translate({_idx*self.row_metadata_cell_width + self.row_metadata_cell_width/2},-3) rotate(270)"
                ))

        # Draw the actual cell. We go per row (e.g. per species we plot all metadata in a group)
        # For each row
        for _idx_y, _row_header in enumerate(self.df_A.index):
            _row_cells = []
            _metadata_for_row = self.df_B_dict[_row_header]
            # For each metadata feature in that row
            for _idx_x, _feature in enumerate(self.row_features):
                _metadata_for_feature = self.df_B_dict[_row_header][_feature]
                _row_cells.append(Rect(
                    x=_idx_x*self.row_metadata_cell_width,
                    y=_idx_y*self.cell_height,
                    width=self.row_metadata_cell_width-1,
                    height=self.cell_height-1,
                    fill=self.scales[_feature](_metadata_for_feature),
                    fill_opacity=0.5,
                    elements=[Title(elements=f"[{_row_header}] {_feature}: {_metadata_for_feature}")]
                ))
            _row_group = G(
                elements=[_row_cells],
            )
            _row_groups.append(_row_group)

        _matrix_B_group = G(
            elements=[_row_groups],
            transform=f"translate({(len(self.df_A.iloc[0])+1)*self.cell_width},0)"
        )

        ####################################################
        ## Column metadata: df_C
        ####################################################
        _column_groups = []
        # Print the feature labels on the right
        for _idx, _feature in enumerate(self.column_features):
            _column_groups.append(Text(
                    x=0, y=0,
                    text=_feature,
                    text_anchor="middle",
                    font_size=12,
                    style="dominant-baseline: middle; text-anchor: start;",
                    transform=f"translate({len(self.df_C)*self.cell_width},{_idx*self.column_metadata_cell_height+self.column_metadata_cell_height/2})"
                ))

        # Draw the actual cell. We go per column (e.g. per sample we plot all metadata in a group)
        # For each column
        for _idx_x, _column_header in enumerate(self.df_A):
            _column_cells = []
            _metadata_for_column = self.df_C_dict[_column_header]
            # For each metadata feature in that column
            for _idx_y, _feature in enumerate(self.column_features):
                _metadata_for_feature = self.df_C_dict[_column_header][_feature]
                _column_cells.append(Rect(
                    x=_idx_x*self.cell_width,
                    y=_idx_y*self.column_metadata_cell_height,
                    width=self.cell_width-1,
                    height=self.column_metadata_cell_height-1,
                    fill=self.scales[_feature](_metadata_for_feature),
                    fill_opacity=0.5,
                    elements=[Title(elements=f"[{_column_header}] {_feature}: {_metadata_for_feature}")]
                ))
            _column_group = G(
                elements=[_column_cells],
            )
            _column_groups.append(_column_group)

        _matrix_C_group = G(
            elements=[_column_groups],
            transform=f"translate(0,{len(self.df_A)*self.cell_height})"
        )

        ###########################
        ## Combine everything
        ###########################
        _matrices_group = G(
            elements=[_matrix_A_group, _matrix_B_group, _matrix_C_group],
            transform=f"translate({self.padding_left},{self.padding_top})"
        )

        return _matrices_group

    def to_svg(self):
        return SVG(width=1000, height=550, class_="notebook", elements=[self.to_group()]).as_str()

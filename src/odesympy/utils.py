system_table = "uqsim-371323.uqsim.system"
model_table = "uqsim-371323.uqsim.model"

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode

from PIL import Image

def get_AgGrid(df, multi_selection=True, use_checkbox=False):
    
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",
                                editable=True)
    gb.configure_pagination()
    # gb.configure_side_bar()
    if multi_selection:
        gb.configure_selection('multiple', use_checkbox=use_checkbox)
    else:
        gb.configure_selection('single', use_checkbox=use_checkbox)

    gridOptions = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        data_return_mode=DataReturnMode.FILTERED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        #width='100%',
        #fit_columns_on_grid_load=False
        )
    
    return grid_response
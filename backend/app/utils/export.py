import pandas as pd
from io import BytesIO

def export_to_xml(data):
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return output
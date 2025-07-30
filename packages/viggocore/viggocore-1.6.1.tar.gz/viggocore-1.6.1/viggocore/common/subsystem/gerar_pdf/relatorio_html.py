HEADER_DEFAULT = """
<div>
    <div style="width: 100%; text-align: center">
    <div class="div-header tr-table-bottom">
        <img src={img_url} alt="Avatar" class="avatar">
        <div>
            <h4 style="font-weight: lighter; margin-top: 0px; margin-bottom: 0px; padding-top: 0px; padding-bottom: 0px;">{nome_empresa}</h4>
            <span class="text-bolder fs-large">{titulo}</span>
        </div>
        <span class="text-lighter fs-small">{data_emissao}</span>
    </div>
    <div class="margin-between-horizontal">
        {filtros}
    </div>
    </div>
</div>
"""  # noqa 501

FILTRO_ROW_TEMPLATE = "<b>{descricao}:</b> {valor} | "


TEMPLATE_DEFAULT = """
{style}
<div class="main-style">
    {header}
    {body}
    {footer}
</div>
"""  # noqa 501

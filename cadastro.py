from datetime import date
import io
import os
import textwrap

import streamlit
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Reporte SMG1", page_icon="📄")

CAMINHO_LOGO = "mercado livre.jfif"

# Exibe o logo na tela se o arquivo existir na pasta
if os.path.exists(CAMINHO_LOGO):
    st.image(CAMINHO_LOGO, width=200)

st.title("📄 Reporte SMG1")

if "reportes" not in st.session_state:
    st.session_state.reportes = []


def gerar_imagem_relatorio(reportes):
    """Gera uma imagem PNG no tamanho mínimo de folha A4 (1240x1754 px - 150 DPI)
    com o logo do Mercado Livre no cabeçalho."""
    # Dimensões padrão A4 a 150 DPI (alta legibilidade)
    largura = 1240
    altura_minima_a4 = 1754
    altura_cabecalho = 150
    margem = 45

    try:
        fonte_titulo = ImageFont.truetype("arialbd.ttf", 34)
        fonte_subtitulo = ImageFont.truetype("arial.ttf", 20)
        fonte_negrito = ImageFont.truetype("arialbd.ttf", 24)
        fonte_texto = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        fonte_titulo = ImageFont.load_default()
        fonte_subtitulo = ImageFont.load_default()
        fonte_negrito = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()

    # Prepara os cartões e calcula a altura necessária
    cartoes_preparados = []
    altura_conteudo = altura_cabecalho + margem

    for item in reportes:
        linhas_texto = textwrap.wrap(item["Passagem de Turno"], width=66)
        if not linhas_texto:
            linhas_texto = ["Sem observações."]

        altura_texto = 90 + (len(linhas_texto) * 30)
        altura_card = max(270, altura_texto + 35)

        cartoes_preparados.append((item, linhas_texto, altura_card))
        altura_conteudo += altura_card + 25

    # Garante que a imagem tenha, no mínimo, o tamanho exato de uma folha A4
    altura_total = max(altura_minima_a4, altura_conteudo + margem)

    # Cria a folha branca
    img = Image.new("RGB", (largura, altura_total), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    # --- Cabeçalho com identidade visual e Logo ---
    draw.rectangle([(0, 0), (largura, 125)], fill=(255, 230, 0))  # Amarelo ML
    draw.rectangle([(0, 120), (largura, 125)], fill=(30, 58, 138))  # Linha azul

    x_titulo = margem
    if os.path.exists(CAMINHO_LOGO):
        try:
            logo = Image.open(CAMINHO_LOGO).convert("RGB")
            logo.thumbnail((170, 95))
            y_logo = (120 - logo.height) // 2
            img.paste(logo, (margem, y_logo))
            x_titulo = margem + logo.width + 30
        except Exception:
            pass

    draw.text(
        (x_titulo, 28),
        "REPORTE DE MONITORAMENTO - SMG1",
        fill=(15, 23, 42),
        font=fonte_titulo,
    )
    draw.text(
        (x_titulo, 74),
        f"Total de registros: {len(reportes)}  |  Emitido em: {date.today().strftime('%d/%m/%Y')}",
        fill=(51, 65, 85),
        font=fonte_subtitulo,
    )

    y_atual = altura_cabecalho

    for idx, (item, linhas_texto, altura_card) in enumerate(
        cartoes_preparados, start=1
    ):
        # Cartão do reporte
        draw.rounded_rectangle(
            [(margem, y_atual), (largura - margem, y_atual + altura_card)],
            radius=12,
            fill=(255, 255, 255),
            outline=(203, 213, 225),
            width=2,
        )

        # Área da foto (lado esquerdo ampliada para A4)
        x_foto = margem + 20
        y_foto = y_atual + 20
        tam_foto = 230

        if item["Imagem"] is not None:
            foto = Image.open(io.BytesIO(item["Imagem"])).convert("RGB")
            foto.thumbnail((tam_foto, tam_foto))
            offset_x = x_foto + (tam_foto - foto.width) // 2
            offset_y = y_foto + (tam_foto - foto.height) // 2
            img.paste(foto, (offset_x, offset_y))
        else:
            draw.rectangle(
                [(x_foto, y_foto), (x_foto + tam_foto, y_foto + tam_foto)],
                fill=(241, 245, 249),
                outline=(203, 213, 225),
                width=2,
            )
            draw.text(
                (x_foto + 68, y_foto + 102),
                "Sem foto",
                fill=(100, 116, 139),
                font=fonte_texto,
            )

        # Área dos textos (lado direito)
        x_texto = x_foto + tam_foto + 35
        draw.text(
            (x_texto, y_atual + 24),
            f"#{idx} | Data: {item['Data']} - {item['Turno']}",
            fill=(30, 58, 138),
            font=fonte_negrito,
        )

        # Linha divisória interna discreta
        draw.line(
            [(x_texto, y_atual + 62), (largura - margem - 25, y_atual + 62)],
            fill=(226, 232, 240),
            width=2,
        )

        y_linha = y_atual + 78
        for linha in linhas_texto:
            draw.text(
                (x_texto, y_linha),
                linha,
                fill=(30, 41, 59),
                font=fonte_texto,
            )
            y_linha += 30

        y_atual += altura_card + 25

    # Salva a imagem final em 150 DPI
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", dpi=(150, 150))
    return buffer.getvalue()


# --- Formulário de Reporte ---
with st.form("form_reporte", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        data_reporte = st.date_input(
            "Data do Reporte *",
            value=date.today(),
            format="DD/MM/YYYY",
        )
    with col2:
        turno = st.selectbox(
            "Turno *",
            ["1º Turno (Manhã)", "2º Turno (Tarde)", "3º Turno (Noite)"],
        )

    with col1:
        turno = st.selectbox(
            "Tipo de Reporte *",
            ["Hora a Hora", "OOT", "Outros"],
        )

    passagem_turno = st.text_area(
        "Passagem de Turno *",
        placeholder="Descreva as ocorrências, status da operação e pendências para o próximo turno...",
        height=140,
    )

    imagem = st.file_uploader(
        "Evidência / Imagem (opcional)",
        type=["png", "jpg", "jpeg", "webp", "jfif"],
    )

    salvar = st.form_submit_button("Registrar Reporte")

# --- Processamento ---
if salvar:
    if passagem_turno.strip():
        dados_imagem = imagem.getvalue() if imagem is not None else None

        st.session_state.reportes.append({
            "Data": data_reporte.strftime("%d/%m/%Y"),
            "Turno": turno,
            "Passagem de Turno": passagem_turno.strip(),
            "Imagem": dados_imagem,
        })
        st.success("Reporte registrado com sucesso!")
    else:
        st.warning("Preencha o campo de Passagem de Turno antes de registrar.")

# --- Exibição dos Reportes e Botão de Download ---
st.divider()
st.subheader(f"Reportes Registrados ({len(st.session_state.reportes)})")

if st.session_state.reportes:
    imagem_relatorio = gerar_imagem_relatorio(st.session_state.reportes)
    st.download_button(
        label="📥 Baixar Reporte em Imagem A4 (PNG)",
        data=imagem_relatorio,
        file_name=f"reporte_smg1_{date.today().strftime('%d_%m_%Y')}.png",
        mime="image/png",
        use_container_width=True,
    )

    dados_tabela = [
        {k: v for k, v in item.items() if k != "Imagem"}
        for item in st.session_state.reportes
    ]
    st.dataframe(dados_tabela, use_container_width=True)

    st.write("### Detalhes e Evidências")
    for idx, item in enumerate(st.session_state.reportes, start=1):
        col1, col2 = st.columns([1, 3])
        with col1:
            if item["Imagem"] is not None:
                st.image(item["Imagem"], use_container_width=True)
            else:
                st.info("Sem imagem anexada")
        with col2:
            st.write(f"**#{idx} — {item['Data']} ({item['Turno']})**")
            st.write(item["Passagem de Turno"])
        st.divider()
else:
    st.info("Nenhum reporte registrado ainda.")
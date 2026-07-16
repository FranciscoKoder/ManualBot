import sys
import json
from pathlib import Path
import fitz
import random

def extrair_frase_de(pdf_path: Path) -> dict:
    """Sorteia uma página de UM PDF específico (passado como argumento)
    e extrai uma frase de verdade usando PyMuPDF."""
    doc = fitz.open(pdf_path)
    pagina_num = random.randint(0, doc.page_count - 1)
    texto = doc[pagina_num].get_text().strip()
    total_paginas = doc.page_count
    doc.close()

    frases = [f.strip() for f in texto.split(".") if len(f.strip()) > 30]
    frase = random.choice(frases) if frases else "(página sem frase longa, tente de novo)"

    return {
        "documento": pdf_path.name,
        "pagina": pagina_num + 1,
        "total_paginas": total_paginas,
        "frase": frase,
    }


def extrair_frase_aleatoria():
    """Sorteia um PDF real de docs/PDFs-Instrucoes e chama extrair_frase_de."""
    projeto_raiz = Path(__file__).resolve().parents[2]
    pasta_pdfs = projeto_raiz / "docs" / "PDFs-Instrucoes"
    pdfs = list(pasta_pdfs.glob("*.pdf"))

    if not pdfs:
        return None

    pdf_escolhido = random.choice(pdfs)
    return extrair_frase_de(pdf_escolhido)

def extract_pdf(pdf_path: Path) -> dict:
    doc= fitz.open(pdf_path)
    pages_info=[]
    problem_pages=[]
    
    for i, page in enumerate(doc):
        text=page.get_text().strip()
        images = page.get_images(full=True)
        drawings = page.get_drawings()
        n_drawings = len(drawings)
        n_curves = sum(1 for d in drawings for op in d.get("items",[]) if op[0] == "c")
        tables_hint = text.count("|")>5 or text.count("\t")>5

        
        has_visual_content = len(images) > 0 or n_curves > 3
        is_scan_suspect = len(text) < 40 and has_visual_content
        is_diagram_heavy = n_curves > 3 or n_drawings > 300

        if is_scan_suspect:
            problem_pages.append(
                {"page": i + 1, "reason": "pouco texto + conteúdo visual (possível página escaneada)"}
            )
        elif is_diagram_heavy:
            problem_pages.append(
                {
                    "page": i + 1,
                    "reason": f"provável esquemático (curvas: {n_curves}, traços: {n_drawings}) — informação visual não capturada no texto",
                }
            )

        pages_info.append(
            {
                "page": i + 1,
                "n_chars": len(text),
                "n_images": len(images),
                "n_drawings": n_drawings,
                "n_curves": n_curves,
                "has_table_hint": tables_hint,
            }
        )
    sample_text = ""
    for p in doc:
        t = p.get_text().strip()
        if len(t)>200:
            sample_text=t
            break
    result={
        "file": pdf_path.name,
        "n_pages": doc.page_count,
        "sample_extracted_text": sample_text,
        "pages_summary": pages_info,
        "problem_pages": problem_pages,
    }
    doc.close()
    return result
            
def listar_pdfs(pasta: Path) -> list[Path]:
    return sorted(pasta.glob("*.pdf"))

def escolher_pdfs(pdfs: list[Path]) -> list[Path]:
    print("PDFs encontrados:")
    for i, pdf in enumerate(pdfs,start=1):
        print(f"[{i}] {pdf.name}")
    print(" [0] Processar todos")
    
    escolha = input("\nDigie o número do documento(ou 0 para todos):").strip()
    
    if escolha == "0":
        return pdfs
    try:
        idx=int(escolha) - 1
        return [pdfs[idx]]
    except (ValueError, IndexError):
        print("Opção inválida.")
        sys.exit(1)
        
def main():
    projeto_raiz = Path(__file__).resolve().parents[2]
    pasta_pdfs = projeto_raiz / "docs" / "PDFs-Instrucoes"
    out_dir = projeto_raiz / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs_disponiveis = listar_pdfs(pasta_pdfs)

    if not pdfs_disponiveis:
        print(f"[AVISO] Nenhum PDF encontrado em {pasta_pdfs}")
        sys.exit(1)

    pdfs_para_processar = escolher_pdfs(pdfs_disponiveis)

    for pdf_path in pdfs_para_processar:
        print(f"\n=== Processando {pdf_path.name} ===")
        result = extract_pdf(pdf_path)

        print(f"Páginas: {result['n_pages']}")
        print(f"Páginas com possível problema: {len(result['problem_pages'])}")
        if result["problem_pages"]:
            for pp in result["problem_pages"][:5]:
                print(f"  - página {pp['page']}: {pp['reason']}")

        top_drawings = sorted(result["pages_summary"], key=lambda p: p["n_drawings"], reverse=True)[:3]
        print(f"Páginas com mais traços vetoriais: {top_drawings}")

        print("\nAmostra de texto extraído:\n")
        print(result["sample_extracted_text"][:500], "...")

        out_file = out_dir / f"{pdf_path.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResultado salvo em: {out_file}")

if __name__=="__main__":
    main()

    
        
    

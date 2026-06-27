import { Component } from '@angular/core';
import { RegistroExcel } from '../../models/RegistroExcel';
import * as XLSX from 'xlsx';
import {DecimalPipe} from "@angular/common"

@Component({
  selector: 'app-perguntas',
  imports: [DecimalPipe],
  templateUrl: './perguntas.component.html',
  styleUrl: './perguntas.component.css'
})
export class PerguntasComponent {
  isLoading = false;
  registros: RegistroExcel[] = [];
  porcentagem = 0;
  progresso: number = 0;
  atual: number = 0;
  total: number = 0;

  onFileChange(event: any): void {
    this.resetData();
    const target: DataTransfer = <DataTransfer>(event.target);

    if (target.files.length !== 1) {
      console.error('Selecione apenas um arquivo');
      return;
    }

    const reader: FileReader = new FileReader();

    reader.onload = (e: any) => {
      const binaryStr: string = e.target.result;
      const workbook: XLSX.WorkBook = XLSX.read(binaryStr, { type: 'binary' });

      const sheetName: string = workbook.SheetNames[0];
      const worksheet: XLSX.WorkSheet = workbook.Sheets[sheetName];

      const jsonData: any[] = XLSX.utils.sheet_to_json(worksheet);

      this.registros = jsonData.map(item =>
        {
        return new RegistroExcel(
          item['classificação'],
          item['pergunta'],
          item['alternativa correta'],
          item['alternativa llm']
        )}
      );
    };

    reader.readAsBinaryString(target.files[0]);
  }

  async enviar(){
    this.isLoading = true;
    this.progresso = 0;
    this.total = this.registros.length;
    this.atual = 0;
    this.porcentagem = 0;
    // limpa os resultados anteriores
    this.registros.forEach(r => {
      r.alternativaLLM = '';
    });

    let algoritmo = (<HTMLInputElement>document.getElementById("algoritmo-select")).value;
    let llm = (<HTMLInputElement>document.getElementById("llm-select")).value;
    let tentativas = 0;
    
    for (let i = 0; i < this.total; i++){
      this.atual = i + 1;
      const data = {
        input: {
          input_user: this.registros[i].pergunta,
        },
        config: {
          id: 1,
          algoritmo: algoritmo,
          model_llm: llm,
        }
      };

      await fetch(`http://localhost:8000/chat`, {
        method: "POST",
        body: JSON.stringify(data)
      })
        .then(async response => {
          let resultString = await response.json();
          console.log(resultString)

          this.registros[i].alternativaLLM = resultString.resposta_normalizada;
          this.calcularPorcentagemAcertos();
          tentativas = 0;
        })
        .catch(async erro => {
          console.log(erro)
          this.registros[i].alternativaLLM = '-';
          if (tentativas < 2){
            i--;
          }
          await this.sleep(10000);
        })
        .finally(async () => {
          tentativas++;
          this.progresso = ((i + 1) / this.total) * 100;
          await this.sleep(1000);
        })
    }
    this.isLoading = false;

    this.atual += 1;
  }


  calcularPorcentagemAcertos(): void {
    let resultado = 0;
    if (this.registros && this.registros.length !== 0) {
      const total = this.registros.length;
      const acertos = this.registros.filter(r => r.acertou).length;
      resultado = (acertos / total) * 100;
    } 
    this.porcentagem = resultado;
  }

  resetData(){
    this.isLoading = false;
    this.porcentagem = 0;
    this.progresso = 0;
    this.total = 0;
    this.atual = 0;
  }

  getCorProgresso(): string {
    if (this.progresso < 30) return '#f44336';   // vermelho
    if (this.progresso < 70) return '#ff9800';   // laranja
    return '#4caf50'; // verde
  }
  
  sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

  downloadExcel(): void {
    if (!this.registros || this.registros.length === 0) {
      console.warn('Nenhum dado para exportar');
      return;
    }

    // Converte os dados para JSON no formato esperado
    const data = this.registros.map(r => ({
      'classificação': r.classificacao,
      'pergunta': r.pergunta,
      'alternativa correta': r.alternativaCorreta,
      'alternativa llm': r.alternativaLLM,
      'acertou': r.alternativaCorreta == r.alternativaLLM ? "sim" : "nao"
    }));

    const worksheet: XLSX.WorkSheet = XLSX.utils.json_to_sheet(data);
    const workbook: XLSX.WorkBook = {
      Sheets: { 'Dados': worksheet },
      SheetNames: ['Dados']
    };

    let algoritmo = <HTMLSelectElement>document.getElementById("algoritmo-select");
    let algoritmoText = algoritmo.options[algoritmo.selectedIndex].text

    let llm = <HTMLSelectElement>document.getElementById("llm-select");
    let llmText = llm.options[llm.selectedIndex].text
    
    const dataName = `dados_${algoritmoText}_${llmText}.xlsx`
    XLSX.writeFile(workbook, dataName);
  }
} 
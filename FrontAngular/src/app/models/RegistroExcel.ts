export class RegistroExcel {
    constructor(
        public classificacao: string,
        public pergunta: string,
        public alternativaCorreta: string,
        public alternativaLLM: string,
    ) { }

    get acertou(): boolean {
        return this.alternativaCorreta === this.alternativaLLM;
    }

}
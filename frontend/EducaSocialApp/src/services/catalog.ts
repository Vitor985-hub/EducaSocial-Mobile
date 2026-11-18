export const categories = [
  { id: 1, name: "Assistência Social", image: require("../assets/logofigma.png") },
  { id: 2, name: "Atendimento ao Cidadão", image: require("../assets/logofigma.png") },
  { id: 3, name: "Educação", image: require("../assets/logofigma.png") },
  { id: 4, name: "Mobilidade", image: require("../assets/logofigma.png") },
  { id: 5, name: "Moradia", image: require("../assets/logofigma.png") },
  { id: 6, name: "Renda", image: require("../assets/logofigma.png") },
  { id: 7, name: "Trabalho", image: require("../assets/logofigma.png") },
];

export const regions = [
  { id: 1, name: "Brasil" },
  { id: 2, name: "Acre" },
  { id: 3, name: "Alagoas" },
  { id: 4, name: "Amapá" },
  { id: 5, name: "Amazonas" },
  { id: 6, name: "Bahia" },
  { id: 7, name: "Ceará" },
  { id: 8, name: "Distrito Federal" },
  { id: 9, name: "Espírito Santo" },
  { id: 10, name: "Goiás" },
  { id: 11, name: "Maranhão" },
  { id: 12, name: "Mato Grosso" },
  { id: 13, name: "Mato Grosso do Sul" },
  { id: 14, name: "Minas Gerais" },
  { id: 15, name: "Pará" },
  { id: 16, name: "Paraíba" },
  { id: 17, name: "Paraná" },
  { id: 18, name: "Pernambuco" },
  { id: 19, name: "Piauí" },
  { id: 20, name: "Rio de Janeiro" },
  { id: 21, name: "Rio Grande do Norte" },
  { id: 22, name: "Rio Grande do Sul" },
  { id: 23, name: "Rondônia" },
  { id: 24, name: "Roraima" },
  { id: 25, name: "Santa Catarina" },
  { id: 26, name: "São Paulo" },
  { id: 27, name: "Sergipe" },
  { id: 28, name: "Tocantins" },
];

export const services = [
  {
    id: 1,
    categoryId: 6,
    name: "CadÚnico — Cadastro Único (Prefeitura de São Paulo)",
    description:
      "O CadÚnico reúne as famílias de baixa renda do país e permite participar de programas sociais federais, estaduais e municipais, como o Programa Bolsa Família, o BPC e a Tarifa Social de Energia Elétrica e Água.",
    regions: 26
  },
  {
    id: 2,
    categoryId: 1,
    name: "Bolsa Família",
    description:
      "O Programa Bolsa Família é um programa de transferência de renda do Governo Federal que tem como objetivo garantir a segurança alimentar e nutricional das famílias em situação de pobreza e extrema pobreza.",
    regions: 1
  },
  {
    id: 3,
    categoryId: 6,
    name: "BPC — Benefício de Prestação Continuada",
    description:
      "O Benefício de Prestação Continuada (BPC) é um benefício assistencial pago pelo Governo Federal a pessoas com deficiência e idosos com 65 anos ou mais que não têm condições de se sustentar.",
    regions: 1
  },
  {
    id: 4,
    categoryId: 5,
    name: "Tarifa Social de Energia Elétrica",
    description:
      "A Tarifa Social de Energia Elétrica é um benefício do Governo Federal que concede descontos na conta de energia elétrica para famílias de baixa renda.",
    regions: 1
  },
  {
    id: 5,
    categoryId: 5,
    name: "Tarifa Social de Água",
    description:
      "A Tarifa Social de Água é um benefício do Governo Federal que concede descontos na conta de água para famílias de baixa renda.",
    regions: 1
  },
  {
    id: 6,
    categoryId: 4,
    name: "Bilhete Único da Pessoa Idosa — gratuidade no transporte (SPTrans)",
    description: "O Bilhete Único da Pessoa Idosa é um benefício do Governo Municipal de São Paulo que garante a gratuidade no transporte público para pessoas com 60 anos ou mais.",
    regions: 26
  },
  {
    id: 7,
    categoryId: 4,
    name: "Atende+ — transporte porta a porta gratuito (SPTrans)",
    description: "O Atende+ é um serviço de transporte público gratuito oferecido pelo Governo Municipal de São Paulo para pessoas com deficiência ou mobilidade reduzida, que não podem utilizar o transporte coletivo convencional.",
    regions: 26
  },
  {
    id: 8,
    categoryId: 3,
    name: "Bilhete Único de Estudante (SPTrans)",
    description: "O Bilhete Único de Estudante é um benefício do Governo Municipal de São Paulo que garante a gratuidade no transporte público para estudantes.",
    regions: 26
  }
];

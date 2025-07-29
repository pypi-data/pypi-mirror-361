import re
from ..interface import searcher

class ResultTable:
   def __init__(self, header: list[str], data: list[list] = []):
      self._header = header.copy()
      self._data = data.copy()
      self.join_fail = False

   # Métodos para Acesso Seguro
   @property
   def header(self):
      return self._header.copy()

   def header_index(self, column_name: str) -> int:
      try:
         return self._header.index(column_name)
      except ValueError:
         raise ValueError(f'The Column name "{column_name}" does not belong in the Result Table Header.')
   
   def verify_row_index(self, index: int):
      if index > (len(self._data) - 1):
         raise IndexError(f'The Row index {index} is out of the Result Table range.')

   # Métodos de Linhas e Colunas
   def column_count(self) -> int:
      return len(self._header)

   def row_count(self) -> int:
      return len(self._data)

   def column(self, name: str) -> list:
      index = self.header_index(name)
      column_data = [row[index] for row in self._data]
      return column_data
      
   def row(self, index: int) -> dict:
      self.verify_row_index(index)
      row_data = {key: value for key, value in zip(self._header, self._data[index])}
      return row_data
   
   def cell(self, column_name: str, row_index) -> str:
      row = self.row(row_index)
      cell = row[column_name]
      return cell
   
   def columns(self):
      for name in self._header:
         yield self.column(name)

   def rows(self):
      for index in range(self.row_count()):
         yield self.row(index)

   def add_row(self, row_data: dict):
      try:
         data_list = [row_data[column_name] for column_name in self._header]
      except KeyError:
         raise KeyError('The Result Table Row Data must contain all header keys.')
      self._data.append(data_list)

   def add_column(self, name: str, default_data):
      self._header.append(name)
      for row in self._data:
         row.append(default_data)

   def delete_row(self, index: int):
      self.verify_row_index(index)
      del self._data[index]
   
   def delete_column(self, name: str):
      index = self.header_index(name)
      del self._header[index]
      for row in self._data:
         del row[index]

   def filter_rows(self, values: dict) -> list[dict]:
      result_rows = self.rows()
      for column, value in values.items():
         result_rows = list(filter(lambda row: row[column] == value, result_rows))
      return result_rows

   # Métodos de Interação com Tabela
   def reorder(self, names: list[str]):
      try:
         data = [[row[name] for name in names] for row in self.rows()]
      except KeyError:
         raise ValueError('Only column names belonging to the Result Table Header must be passed.')
      self._header = names.copy()
      self._data = data.copy()

   def join(self, table):
      # Initializando Variável de Controle para a Falha do Método
      self.join_fail = False

      # Tradando Caso Simples de Tabela Vazia
      if self.column_count() == 0:
         return table

      # Avaliando Atributos Compartilhados pelas Tabelas
      table_1, table_2 = self, table
      attributes_1 = set(table_1._header)
      attributes_2 = set(table_2._header)
      shared_attributes = list(attributes_1 & attributes_2)
      
      # Conservando Tabela Atual Caso não Haja Atributos Compartilhados
      if len(shared_attributes) == 0:
         self.join_fail = True
         return table_1

      # Avaliando se uma das Tabelas já Contém a Outra
      if len(self._header) == len(shared_attributes):
         return table
      if len(table._header) == len(shared_attributes):
         return self
      
      # Instanciando Nova Tabela com todos os Atributos
      joined_columns = list(attributes_1 | attributes_2)
      joined_table = ResultTable(joined_columns)
      
      # Juntando Linhas
      for row_1 in table_1.rows():
         values = {a: row_1[a] for a in shared_attributes}
         rows_2 = table_2.filter_rows(values)
         for row_2 in rows_2:
            row_1.update(row_2)
            joined_table.add_row(row_1)

      return joined_table

   # Métodos de Conversão de Dados da Tabela
   def to_csv(self):
      csv_data = ','.join(self._header)
      for row in self.rows():
         csv_data += '\n' + ','.join(row.values())
      return csv_data

class Operator:
   # Métodos de Avaliação dos Operadores
   def in_evaluate(value, test: str, type_class):
      params = test.split(':')
      len_params = len(params)

      # Caso Onde o Formato dos Parâmetros do Valor de Teste é Inválido
      if len_params > 3 or len_params < 2:
         raise ValueError('The right operand of the "in" operator has a invalid format (it must be [start]:[stop] or [start]:[stop]:[step], all of these integers).')
      
      # Verificando se Todos os Parâmetros são Inteiros
      try:
         params = list(map(int, params))
      except ValueError:
         raise ValueError('All numbers in the right operand of the "in" operator must be integers.')
      
      return type_class(value) in range(*params)

   supported_operators = {
      'and': {
         'type': 'logical',
         'evaluate': lambda c1, c2, av, at: c1.approve(av, at) and c2.approve(av, at)
      },
      'or': {
         'type': 'logical',
         'evaluate': lambda c1, c2, av, at: c1.approve(av, at) or c2.approve(av, at)
      },
      '=': {
         'type': 'relational',
         'evaluate': lambda v, t, tc: tc(v) == tc(t)
      },
      '>': {
         'type': 'relational',
         'evaluate': lambda v, t, tc: tc(v) > tc(t)
      },
      '<': {
         'type': 'relational',
         'evaluate': lambda v, t, tc: tc(v) < tc(t)
      },
      '<=': {
         'type': 'relational',
         'evaluate': lambda v, t, tc: tc(v) <= tc(t)
      },
      '>=': {
         'type': 'relational',
         'evaluate': lambda v, t, tc: tc(v) >= tc(t)
      },
      '!=': {
         'type': 'relational',
         'evaluate': lambda v, t, tc: tc(v) != tc(t)
      },
      'in': {
         'type': 'relational',
         'evaluate': in_evaluate
      }
   }

   def __init__(self, symbol: str):
      try:
         operator = Operator.supported_operators[symbol]
         self.type = operator['type']
         self.evaluate = operator['evaluate']
      except KeyError:
         raise KeyError(f'Unsupported operator "{symbol}" was used.')
   
class Condition:
   def __init__(self, condition_expression: str = None, conditioned_attributes: set = set()):
      # Verificando se a Condição é Nula
      self.is_none_condition = condition_expression is None
      if not self.is_none_condition:
         # Inicializando Conjunto Compartilhado de Atributos Condicionados
         self.conditioned_attributes = conditioned_attributes

         # Buscando Operador na Expressão
         for supported_operator in Operator.supported_operators.keys():
            operands = condition_expression.split(f' {supported_operator} ', 1)
            if len(operands) > 1:
               break
         else:
            raise KeyError('A Condition has not a supported operator.')
         
         # Instanciando Operador e Operandos
         self.operator = Operator(supported_operator)
         if self.operator.type == 'logical':
            self.operand_1 = Condition(operands[0], self.conditioned_attributes)
            self.operand_2 = Condition(operands[1], self.conditioned_attributes)
         else:
            self.conditioned_attributes.add(operands[0])
            self.operand_1 = operands[0]
            self.operand_2 = operands[1]
      
   def approve(self, attribute_values: dict, attribute_types: dict) -> bool:
      # Verificando se a Condição é Nula
      if not self.is_none_condition:
         # Avaliando Condição Lógica
         if self.operator.type == 'logical':
            # Verificano se há Atributos Condicionáveis nos Valores Passados
            set_attributes = set(attribute_values.keys())
            set_conditioned = set(self.conditioned_attributes)
            set_conditionable = set_attributes & set_conditioned

            # Avaliar com Operador se Há Atributos Condicionáveis
            if len(set_conditionable) > 0:
               return self.operator.evaluate(self.operand_1, self.operand_2, attribute_values, attribute_types)
         
         # Avaliando Condição Relacional
         else:
            if self.operand_1 in attribute_values.keys():
               type_class = attribute_types[self.operand_1]
               value = attribute_values[self.operand_1]
               test = self.operand_2
               return self.operator.evaluate(value, test, type_class)
      
      # Retornando True por Padrão
      return True

class Attribute:
   type_relations = {
      'str': str,
      'int': int,
      'float': float,
      'list': list
   }
   extraction_attributes = searcher.get_database('extraction_attributes')

   def __init__(self, name: str):
      # Extraindo Informações do Atributo da Database
      try:
         # Extraindo Index Informado para o Atributo se Houver
         self.name = name
         attribute_index = None
         if result := re.match('([\w.]+)\[(-?\d+)\]', name):
            name = result.group(1)
            attribute_index = int(result.group(2))

         # Atribuindo Informações ao Atributo com base na Database
         info = Attribute.extraction_attributes[name]
         self.format = info['format']

         # Verificando se atributos do tipo "list" tiveram um index informado
         self.type = Attribute.type_relations[info['data_type']]
         if self.type is list:
            if attribute_index is not None:
               self.index = attribute_index
               self.sub_type = Attribute.type_relations[info['sub_type']]
            else:
               raise SyntaxError(f'The Attribute "{name}" must have an associated index.')
            
         # Organizando Atributos Relacionados
         self.related_attributes = dict()
         for related_attribute in info['related_attributes']:
            data_type =  Attribute.extraction_attributes[related_attribute]['data_type']
            type_class = Attribute.type_relations[data_type]
            self.related_attributes[related_attribute] = type_class

      except KeyError:
         raise KeyError(f'Unsupported attribute "{name}" was used.')

   def extract_from(self, pos_data: str, condition: Condition):
      # Instanciando Tabela de Resultado
      result_table = ResultTable([self.name, *self.related_attributes])

      # Extraindo Dados a partir das Keywords
      keyword_matches = re.finditer(self.format['keywords'], pos_data)
      for keyword_match in keyword_matches:
         # Identificando Atributos Relacionados ao Atual a Nível de Keyword
         keyword_related = keyword_match.groupdict()
         line_data = keyword_related.pop('line')
         line_matches = re.finditer(self.format['line'], line_data, re.MULTILINE)

         # Extraindo Dados a partir das Linhas de Keyword
         for line_match in line_matches:
            # Identificando Atributos Relacionados ao Atual a Nível de Linha
            line_related = line_match.groupdict()
            value = line_related.pop('value')

            # Tratamento Especial para Atributos do Tipo "list"
            if self.type is list:
               try:
                  value = value.split()[self.index]
               except IndexError:
                  raise IndexError(f'The Index "[{self.index}]" is out of range in "{self.name}".')

            # Combinando Atributos Relacionados
            line_related.update(keyword_related)

            # Criando Dicionários com Todos os Valores do Atributo (Próprio e Relacionados)
            attribute_values = dict()
            attribute_values[self.name] = value
            for key, value in line_related.items():
               attribute_values[key.replace('_', '.')] = value

            # Criando Dicionários com Todos os Tipos do Atributo (Próprio e Relacionados)
            attribute_types = dict()
            attribute_types[self.name] = self.type if (self.type is not list) else self.sub_type
            attribute_types.update(self.related_attributes)

            # Aprovando ou Não Valores para a Tabela de Resultado com Base na Condição
            if condition.approve(attribute_values, attribute_types):
               result_table.add_row(attribute_values)
      
      return result_table

   def change_to(self, value_to_change: str, dat_data: str, condition: Condition):
      # Verificando se Atributos Condicionados são Relacionados com o Atributo a ser Alterado
      related_attributes = set(self.related_attributes.keys())
      related_attributes.add(self.name)
      if (
         (not condition.is_none_condition) and 
         (len(condition.conditioned_attributes | related_attributes) > len(related_attributes))
      ):
         raise KeyError('All Conditioned Attributes must be related to the Attribute that will be changed.') 

      # Percorrendo Keywords do Atributo
      keyword_matches = re.finditer(self.format['keywords'], dat_data)
      for keyword_match in keyword_matches:
         # Identificando Atributos Relacionados ao Atual a Nível de Keyword
         keyword_related = keyword_match.groupdict()
         line_data = keyword_related.pop('line')
         line_matches = re.finditer(self.format['line'], line_data, re.MULTILINE)

         # Extraindo Dados a partir das Linhas de Keyword
         new_line_data = line_data
         for line_match in line_matches:
            # Identificando Atributos Relacionados ao Atual a Nível de Linha
            line_related = line_match.groupdict()
            value = line_related.pop('value')

            # Tratamento Especial para Atributos do Tipo "list"
            if self.type is list:
               try:
                  value = value.split()[self.index]
               except IndexError:
                  raise IndexError(f'The Index "[{self.index}]" is out of range in "{self.name}".')

            # Combinando Atributos Relacionados
            line_related.update(keyword_related)

            # Criando Dicionários com Todos os Valores do Atributo (Próprio e Relacionados)
            attribute_values = dict()
            attribute_values[self.name] = value
            for key, value in line_related.items():
               attribute_values[key.replace('_', '.')] = value

            # Criando Dicionários com Todos os Tipos do Atributo (Próprio e Relacionados)
            attribute_types = dict()
            attribute_types[self.name] = self.type if (self.type is not list) else self.sub_type
            attribute_types.update(self.related_attributes)

            # Aprovando ou Não Valores para a Alteração com Base na Condição
            if condition.approve(attribute_values, attribute_types):
               # Instanciando Linha Antiga e Linha Nova
               old_line = line_match.group()
               new_line = self.format['line']

               # Substituindo Formatos Regex pelos Valores para a Nova Linha
               attribute_values.pop(self.name)
               attribute_values['value'] = value_to_change
               for name, value in attribute_values.items():
                  name = name.replace('.', '_')
                  new_line = re.sub(f'\(\?P<{name}>[^\)]+[^\(]+\)', value, new_line)
               new_line = new_line.replace('\s+', '   ')
               
               # Substituindo Linha Antiga pela Nova no Conjunto de Linhas
               new_line_data = new_line_data.replace(old_line, new_line)

         # Substituindo Conjunto de Linhas Antigo pelo Novo no .dat
         dat_data = dat_data.replace(line_data, new_line_data)

      return dat_data

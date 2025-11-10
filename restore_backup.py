import json
import psycopg2
from pathlib import Path

def restore_backup(backup_file, database_name='photoskeka_db', host='localhost', port=5432, user='photoskeka_carlos', password='calberto'):
    """
    Restaura backup de tabelas de um arquivo JSON para um banco PostgreSQL
    
    Args:
        backup_file: Caminho do arquivo backup.json
        database_name: Nome do banco de dados (ex: photoskeka_db)
        host: Host do PostgreSQL (padrão: localhost)
        port: Porta do PostgreSQL (padrão: 5432)
        user: Uphotoskeka_carlos (padrão: postgres)
        password: calberto
    """
    
    # Verifica se o arquivo de backup existe
    if not Path(backup_file).exists():
        print(f"Erro: Arquivo {backup_file} não encontrado!")
        return False
    
    try:
        # Lê o arquivo de backup
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"Backup carregado com sucesso de {backup_file}")
        print(f"Tabelas encontradas: {list(backup_data.keys())}")
        
        # Conecta ao banco de dados PostgreSQL
        conn = psycopg2.connect(
            dbname=database_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cursor = conn.cursor()
        
        # Para cada tabela no backup
        for table_name, records in backup_data.items():
            print(f"\nRestaurando tabela: {table_name}")
            print(f"Registros a restaurar: {len(records)}")
            
            if not records:
                print(f"  Nenhum registro para restaurar em {table_name}")
                continue
            
            # Limpa a tabela existente (opcional - comente se quiser manter dados)
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"  Tabela {table_name} limpa")
            
            # Obtém as colunas do primeiro registro
            columns = list(records[0].keys())
            placeholders = ', '.join([f'%s' for _ in columns])
            columns_str = ', '.join(columns)
            
            # Insere os registros
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            restored_count = 0
            for record in records:
                try:
                    values = [record[col] for col in columns]
                    cursor.execute(insert_query, values)
                    restored_count += 1
                except psycopg2.Error as e:
                    print(f"  Erro ao inserir registro: {e}")
                    continue
            
            print(f"  ✓ {restored_count} registros restaurados em {table_name}")
        
        # Commit das alterações
        conn.commit()
        print(f"\n✓ Backup restaurado com sucesso no banco {database_name}!")
        
        # Exibe estatísticas
        print("\n--- Estatísticas do Banco ---")
        for table_name in backup_data.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} registros")
        
        cursor.close()
        conn.close()
        return True
        
    except json.JSONDecodeError as e:
        print(f"Erro ao ler JSON: {e}")
        return False
    except psycopg2.Error as e:
        print(f"Erro no banco de dados PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


# Exemplo de uso
if __name__ == "__main__":
    # Configure suas credenciais do PostgreSQL
    restore_backup(
        backup_file='backup.json',
        database_name='photoskeka_db',
        host='localhost',
        port=5432,
        user='photoskeka_carlos',
        password='calberto'
    )
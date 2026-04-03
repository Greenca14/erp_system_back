import logging
from decimal import Decimal
from lxml import etree
from .models import Company, Employee, Course

logger = logging.getLogger(__name__)

def run_xml_import(file_content):
    """
    Основная функция парсинга. Разделяет логику в зависимости от корневого тега XML.
    """
    try:
        root = etree.fromstring(file_content)
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag

        if tag == 'Edu_Participant':
            return _parse_participant(root)
        elif tag == 'Edu_Course':
            return _parse_course(root)
        else:
            logger.warning(f"Обнаружен неизвестный тег XML: {tag}")
    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге XML: {str(e)}")

def _parse_participant(root):
    """
    Парсинг участника обучения и автоматическое создание/связь с Компанией[cite: 8, 13, 48].
    """
    xml_id = root.findtext('id')
    fio = root.findtext('sFIO')
    org_name = root.findtext('idOrganizationHL')
    org_code_raw = root.findtext('sCode')
    
    org_code = org_code_raw[:4] if org_code_raw else "TEMP"

    company, _ = Company.objects.get_or_create(
        code=org_code,
        defaults={'name': org_name or f"Компания {org_code}"}
    )
    employee, created = Employee.objects.update_or_create(
        email=f"user_{xml_id}@erp.local", 
        defaults={
            'full_name': fio,
            'company': company,

        }
    )
    status = "создан" if created else "обновлен"
    logger.info(f"Сотрудник {fio} {status}. Связан с компанией {company.code}.")
    return f"Участник {fio} обработан."

def _parse_course(root):
    """
    Парсинг курса с сохранением цены и длительности для расчетов стоимости[cite: 9, 16, 53].
    """
    title = root.findtext('sCourseHL')
    
    try:
        duration = int(root.findtext('nDurationInDays') or 0)
        price = Decimal(root.findtext('nPricePerPerson') or '0.00')
    except (ValueError, TypeError):
        duration, price = 0, Decimal('0.00')
        logger.error(f"Ошибка форматов чисел в курсе: {title}")

    course, created = Course.objects.update_or_create(
        title=title,
        defaults={
            'description': root.findtext('sDescription') or "",
            'duration_days': duration,
            'base_price': price
        }
    )
    logger.info(f"Курс '{title}' сохранен. Цена: {price} руб. [cite: 53]")
    return f"Курс {title} обработан."
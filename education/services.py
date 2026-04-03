import logging
from decimal import Decimal
from lxml import etree
from .models import Company, Employee, Course

logger = logging.getLogger(__name__)

def run_xml_import(file_content):
    """
    Основная функция парсинга.
    """
    try:
        root = etree.fromstring(file_content)
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag

        if tag in ['Edu_Employee', 'Edu_Participant']:
            return _parse_employee(root)
        elif tag == 'Edu_Course':
            return _parse_course(root)
        else:
            logger.warning(f"Обнаружен неизвестный тег XML: {tag}")
    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге XML: {str(e)}")

def _parse_employee(root):
    """
    Парсинг участника. Используем sCode для связи с компанией.
    """
    xml_id = root.findtext('id')
    fio = root.findtext('sFIO')
    org_name = root.findtext('idOrganizationHL')
    org_code = root.findtext('sCode') or "TEMP"

    # Создаем компанию (используем sCode как уникальный ключ)
    company, _ = Company.objects.get_or_create(
        code=org_code,
        defaults={'name': org_name or f"Компания {org_code}"}
    )
    
    # Создаем сотрудника
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
    Парсинг курса с сохранением цены и длительности для расчетов стоимости
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
    logger.info(f"Курс '{title}' сохранен. Цена: {price} руб.")
    return f"Курс {title} обработан."


def export_employee_to_xml(employee_id):
    """
    Экспорт сотрудника в формате Edu_Employee
    """
    employee = Employee.objects.select_related('company').get(id=employee_id)

    root = etree.Element("Edu_Employee")
    etree.SubElement(root, "id").text = str(employee.id)
    etree.SubElement(root, "sCode").text = employee.company.code
    etree.SubElement(root, "sFIO").text = employee.full_name
    etree.SubElement(root, "idOrganization").text = None
    etree.SubElement(root, "idOrganizationHL").text = employee.company.name
    
    return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

def export_course_to_xml(course_id):
    """
    Экспорт курса в формате Edu_Course
    """
    course = Course.objects.get(id=course_id)
    
    root = etree.Element("Edu_Course")
    etree.SubElement(root, "id").text = str(course.id)
    etree.SubElement(root, "sCode").text = None
    etree.SubElement(root, "sCourseHL").text = course.title
    etree.SubElement(root, "sDescription").text = course.description or ""
    etree.SubElement(root, "nDurationInDays").text = str(course.duration_days)
    etree.SubElement(root, "nPricePerPerson").text = str(course.base_price)
    
    return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)
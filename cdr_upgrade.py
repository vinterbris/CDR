import sys, re

if len(sys.argv) > 1:
    if sys.argv[1] == "-t":
        print("TEST\n")
    elif sys.argv[1] == "-p":
        print("PROD/MINI\n")
else:
    # для тестовых запусков без флага
    sys.argv.append("-t")


# Путь к папке для сохранения файлов
cdr_folder_path = 'c:/Users/svdobrovolskiy/Documents/!SONUP/#sanity_test/'

def main():
    release_number = input('Номер релиза?: ')
    file_name = cdr_folder_path + release_number + ".txt"
    print('\nФормирование CDR команд\n')
    # Запросить номера заказов
    print('Номера заказов')
    vmware, openstack, xvdc_vmware, xvdc_openstack = get_orders()
    # Составить 3 списка родительские + дочерние, только родительские, только дочерние заказы
    full_orders_list, main_orders_list, child_orders_list = get_orders_list(vmware, openstack, xvdc_vmware, xvdc_openstack)
    # Составить CDR команды
    CdrCollectService, CDRexport = form_cdr(full_orders_list, main_orders_list)
    # Записать в файл исходные значения родительских и дочерних заказов и итоговые команды
    with open(file_name, "w") as file:
        file.write(f"Номера родительских заказов: vmware {vmware}, openstack {openstack}, xvdc_vmware {xvdc_vmware}, xvdc_openstack {xvdc_openstack}\n")
        file.write(f"Номера дочерних заказов: {child_orders_list}\n")
        file.write(f"{CdrCollectService}\n")
        file.write(f"{CDRexport}\n")
        # cdr_result = input("Сохранить выгрузку: ")
        # file.write(cdr_result)
    print(f'\nФайл {file_name} с результатом создан')

def clear(order):
    return re.sub("-.*", "", order)

def get_child_orders(order, virtualisation_type):
    # Запросить номера дочерних заказов узких ЦОД-ов vmware и openstack
    print(f'\n\nКоманда получения дочерних заказов:\nOrchestrator::Models::Order.find({order}).child_orders.map(&:id)')
    return input(f'\nНомера дочерних заказов {virtualisation_type}: ')

def get_orders():
    # Для теста запрашиваем все номера заказов
    if sys.argv[1] == "-t":
        try:
            vmware = int(input('vdc vmware: '))
        except:
            vmware = ""
        try:
            openstack = int(input("vdc openstack: "))
        except:
            openstack = ""
        try:
            xvdc_vmware = int(input("xvdc vmware: "))
        except:
            xvdc_vmware = ""
        try:
            xvdc_openstack = int(input("xvdc openstack: "))
        except:
            xvdc_openstack = ""
    # Для прода запрашиваем только один номер заказа
    elif sys.argv[1] == "-p":
        try:
            vmware = int(input('vdc vmware: '))
        except:
            vmware = ""
        openstack = ""
        xvdc_vmware = ""
        xvdc_openstack = ""
    return vmware, openstack, xvdc_vmware, xvdc_openstack

def get_orders_list(vmware, openstack, xvdc_vmware, xvdc_openstack):
    full_orders_list = []
    main_orders_list = []
    child_orders_list = []
    if vmware != "":
        child_orders_vmware = get_child_orders(vmware, "vmware").split(",")
        full_orders_list.append(vmware)
        main_orders_list.append(vmware)
        child_orders_list.append("vmware")
        for i in child_orders_vmware:
            full_orders_list.append(int(i))
            child_orders_list.append(int(i))
    if openstack != "":
        child_orders_openstack = get_child_orders(openstack, "openstack").split(",")
        full_orders_list.append(openstack)
        main_orders_list.append(openstack)
        child_orders_list.append("openstack")
        for i in child_orders_openstack:
            full_orders_list.append(int(i))
            child_orders_list.append(int(i))
    if xvdc_vmware != "":
        full_orders_list.append(xvdc_vmware)
        main_orders_list.append(xvdc_vmware)
    if xvdc_openstack != "":
        full_orders_list.append(xvdc_openstack)
        main_orders_list.append(xvdc_openstack)
    return full_orders_list, main_orders_list, child_orders_list

def form_cdr(full_orders_list, main_orders_list):
    '''
    Пример итоговых команд:
        CdrCollectService::Endpoint.new(id: [82920, 82921, 82922, 82925]).call  
        CDR.export(filter:{primary_order_id: [82920]})
    '''
    # Сформировать и вывести CDR.collect
    CdrCollectService = f"\n\nCdrCollectService::Endpoint.new(id: {full_orders_list}).call"
    print(CdrCollectService)
    # Сформировать и вывести CDR.export
    CDRexport = f"CDR.export(filter:{{primary_order_id: {main_orders_list}}})"
    print(CDRexport)
    return CdrCollectService, CDRexport

if __name__ == '__main__':
    main()
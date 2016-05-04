from chromedriverexe import chrome_driver_path
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from tkinter.messagebox import showerror
import time


def close_driver(driver):
    driver.close()
    driver.stop_client()
    driver.quit()


def start_site(urls):
    """
    :param urls: URL for DEV or PROD, pulled from global dictionary in auto_caller.py

    This function stores the URLs for Service-Now to be retrieved.
    Notice how driver.get(url) is called twice. This is because
    Service-Now's single sign on brings Chrome to a framed page,
    and this page cannot be crawled very easily. At least not yet.

    UPDATE: I found out where in the element of a framed page I can pull ID's from.
    But that would require me to get the ID's for all fields again. Coming Soon!
    """

    url = urls

    driver = webdriver.Chrome()
    #driver.set_window_position(-1050, -240)  # This is for my three monitor setup.
    driver.get(url)
    driver.get(url)

    return driver


def get_call_fields(urls):
    """
    :param urls: URL for DEV or PROD, pulled from global dictionary in auto_caller.py

    The following fields are used by the functions in this module.
    The purpose of this module is to de-clutter the GUI .py file.

    These fields are returned for each function to utilize. More to be added!
    """

    driver = start_site(urls)

    caller_field = driver.find_element_by_id("sys_display.new_call.caller")
    call_type = driver.find_element_by_id("new_call.call_type")
    contact_type = driver.find_element_by_id("new_call.contact_type")
    short_desc = driver.find_element_by_id("new_call.short_description")
    long_desc = driver.find_element_by_id("new_call.description")
    submit_call = driver.find_element_by_name("not_important")

    return caller_field, call_type, contact_type, short_desc, long_desc, submit_call, driver


def be_status_update(user, ticket, urls):
    """
    :param user: This contains the username from the user entry in main gui
    :param ticket: This is the ticket number entered from the pop up window
    :param urls: This is the URL to use, choices are DEV and PROD

    :return: No return value.

    This creates and closes a Status update request call.
    """
    caller_field, call_type, contact_type, short_desc, long_desc, submit_call, driver = get_call_fields(urls)

    caller_field.send_keys(user)
    call_type.send_keys('s')
    contact_type.send_keys('p')
    short_desc.send_keys('Status update on %s.' % ticket)
    with open('status_text') as f:
        text = f.read()
    long_desc.send_keys('Status update on {}.\n{}'.format(ticket, text))
    submit_call.click()
    close_driver(driver)


def password_reset_init(nt=False, endpoint=False, doms=False, swms=False, mainframe=False, good=False):
    """
    This function initializes the information needed for the password resets.
    It determines the configuration item and password reset type.
    Then returns the values of those variables.

    :param nt: NT Password Reset workflow.
    :param endpoint: Endpoint Recovery workflow.
    :param doms: DOMS UMS Password resets workflow
    :param swms: SWMS Pincode reset workflow
    :param mainframe: Mainframe (CCE, CIS, etc) password reset workflow.
    :param good: Goodlink password reset workflow

    :return: Returns config_type and reset_type to be used by the call creator.
    """
    # These are the close notes for the password resets.
    close_templates = {'nt': "Logged into NTE293.\nReset User's Password.\nVerified user could log in.",
                       'endpoint': "Performed machine recovery.\nVerified user could log in.",
                       'doms': "Logged into DOMS UMS.\nReset user's password\nVerified user could log in.",
                       'swms': "Logged into NTE293\nStarted SQL Plus for SWMS.\nReset user's pincode.",
                       'mainframe': "Logged into QWS3270\nReset user's password.\nVerified user could log in.",
                       'good': "Logged into Good Mobile Control\nReset user's password.\nVerified user could log in."}

    # This is the dictionary of reset types and their associated texts
    reset_types = {'nt': ('NT Password Reset.', 'ACTIVE DIRECTORY OBJECTS', close_templates['nt']),
                   'endpoint': ('Endpoint Recovery.', 'MCAFEE ENDPOINT ENCRYPTION', close_templates['endpoint']),
                   'doms': ('DOMS UMS Password Reset.', 'DOMS USER MANAGEMENT TOOL', close_templates['doms']),
                   'swms': ('SWMS Pincode Reset.', 'SWMS - SITE WORK MANAGEMENT SYSTEM', close_templates['swms']),
                   'mainframe': ('Mainframe Password Reset.', 'GENERIC MAINFRAME', close_templates['mainframe']),
                   'good': ('Goodlink Password Reset.', 'GOODLINK', close_templates['good'])}

    # Setting reset_type to false to catch any mistakes.
    reset_type = False
    config_type = False
    close_notes = False

    # Checking to see which reset workflow is going to run.
    if nt:
        reset_type = reset_types['nt'][0]
        config_type = reset_types['nt'][1]
        close_notes = reset_types['nt'][2]
    if endpoint:
        reset_type = reset_types['endpoint'][0]
        config_type = reset_types['endpoint'][1]
        close_notes = reset_types['endpoint'][2]
    if doms:
        reset_type = reset_types['doms'][0]
        config_type = reset_types['doms'][1]
        close_notes = reset_types['doms'][2]
    if swms:
        reset_type = reset_types['swms'][0]
        config_type = reset_types['swms'][1]
        close_notes = reset_types['swms'][2]
    if mainframe:
        reset_type = reset_types['mainframe'][0]
        config_type = reset_types['mainframe'][1]
        close_notes = reset_types['mainframe'][2]
    if good:
        reset_type = reset_types['good'][0]
        config_type = reset_types['good'][1]
        close_notes = reset_types['good'][2]

    # Set to false just in case no reset type is called.
    if not reset_type or not config_type or not close_notes:
        showerror('Unexpected Error!', 'Could not determine call type, configuration item, or close notes. '
                                       'Fatal Error. Closing program.')
        quit()

    return reset_type, config_type, close_notes


def password_reset(urls, user, **kwargs):
    """
    This is the bulk for all the password reset options.
    Managed to make it rather easy to expand on.
    Might use this technique for other workflows.

    :param urls: This is the URL for PROD or DEV. It is passed to get_call_fields(urls)
    :param user: This is the user the ticket is being made for. Pulls from uid_entry.
    :param kwargs: Your options are nt, endpoint, doms, swms, mainframe, and good

    :return: Does not return anything. Creates and closes a ticket.
    """
    reset_type, config_type, close_notes = password_reset_init(**kwargs)

    caller_field, call_type, contact_type, short_desc, long_desc, submit_call, driver = get_call_fields(urls)

    # When the call_type is changes, a new field is created.
    # This is a dropdown/search of all workflows.
    req_item = driver.find_element_by_id("sys_display.new_call.request_item")

    # This fills out the call window.
    caller_field.send_keys(user)
    call_type.send_keys('r')
    contact_type.send_keys('p')
    req_item.send_keys('CCC Password Reset')
    long_desc.send_keys(reset_type)
    time.sleep(2)
    submit_call.click()

    # The next few lines are the CCC Password Reset workflow fields.
    config_item = driver.find_element_by_name("sys_display.IO:4e0770f08965f900d9e523fbb346a77b")
    verify_uid = driver.find_element_by_id("IO:35b7852140ac3100f9474a0ce60d98b3")
    order_now = driver.find_element_by_id("order_now")

    # Safe but slow way to set configuration item.
    config_item.send_keys(config_type)
    time.sleep(1)
    config_item.send_keys(Keys.ARROW_DOWN)
    time.sleep(1)
    config_item.send_keys(Keys.ENTER)
    verify_uid.click()
    time.sleep(1)
    order_now.click()

    # Checkout needs to be initialized in order to be clicked on.
    checkout = driver.find_element_by_id("header_button_checkout_in_footer")
    checkout.click()

    # Request link to open workflow.
    request = driver.find_element_by_id("requesturl")
    request.click()

    # Requested Item link to drill down.
    request_item = driver.find_element_by_class_name("formlink")
    request_item.click()

    # Task link to drill down.
    task_link = driver.find_element_by_class_name("formlink")
    task_link.click()

    # From here, the close notes need to be entered
    # And the request needs to be closed out.
    # Maybe another call to the **kwargs to a function that just pumps in close notes.
    work_notes = driver.find_element_by_id("sc_task.work_notes")
    close_task = driver.find_element_by_id("79cc847bc611227d01a8092813683b36")

    # Putting close notes in the ticket and closing the ticket.
    work_notes.send_keys(close_notes)
    close_task.click()

    # Now we gently force the program to self destruct!
    close_driver(driver)


def be_new_cellular_order(user, cell, device, unit, charge, name, urls):

    caller_field, call_type, contact_type, short_desc, long_desc, submit_call, driver = get_call_fields(urls)
    req_item = driver.find_element_by_id("sys_display.new_call.request_item")

    # This field fills out the call
    caller_field.send_keys(user)
    call_type.send_keys('r')
    contact_type.send_keys('p')
    req_item.send_keys('Cellular - New/Upgrade/Accessory/Port')
    time.sleep(.7)
    req_item.send_keys(Keys.ARROW_DOWN)
    time.sleep(.2)
    req_item.send_keys(Keys.ENTER)
    long_desc.send_keys(Keys.LEFT_CONTROL, 'a')
    long_desc.send_keys("NEW SERVICE  {}  {}  {}  RITM#####".format(device.upper(), name.upper(), cell))
    submit_call.click()

    # This fills out the workflow form.
    phone = driver.find_element_by_id("sys_display.IO:59194dfc0a0a3c11467b59a9454a205d")
    new_order = driver.find_element_by_id("IO:8a7cd1dcff5a5084e9b6f056497efef6")
    short_desc = driver.find_element_by_id("IO:23c37554ffda5084e9b6f056497efea1")
    corporate = driver.find_element_by_id("IO:dbd4b594ffda5084e9b6f056497efeae")
    unit_field = driver.find_element_by_id("IO:0cc0bc5f7ddef8002545df1a1ba24f40")
    charge_field = driver.find_element_by_id("IO:42bf2cdb7ddef8002545df1a1ba24f42")
    description = driver.find_element_by_id("IO:8c2c89000a0a3c6f00d3715fafa29704")
    order_now = driver.find_element_by_id("order_now")

    phone.send_keys(cell)
    new_order.click()
    short_desc.send_keys(Keys.LEFT_CONTROL, 'a')
    short_desc.send_keys("NEW SERVICE  {}  {}  {}  RITM#####".format(device.upper(), name.upper(), cell))
    corporate.click()
    unit_field.send_keys(unit)
    charge_field.send_keys(charge)
    description.send_keys(Keys.LEFT_CONTROL, 'a')
    description.send_keys("NEW SERVICE  {}  {}  {}  RITM#####\n"
                          "Requesting {}\n"
                          "Unit: {} Charge: {}".format(device.upper(), name.upper(), cell,
                                                       device.upper(), unit, charge))
    # This puts order in cart.
    time.sleep(2)
    order_now.click()

    # This confirms the order.
    confirm_order = driver.find_element_by_id("header_button_checkout_in_footer")
    confirm_order.click()

    # This drills into the REQ
    request = driver.find_element_by_id("requesturl")
    request.click()

    # This drills into the RITM
    request_item = driver.find_element_by_class_name("formlink")
    request_item.click()

    close_driver(driver)


def be_goodlink_reprovision(user, phone, urls):
    """
    This is a Goodlink reprovision
    """
    caller_field, call_type, contact_type, short_desc, long_desc, submit_call, driver = get_call_fields(urls)
    req_item = driver.find_element_by_id("sys_display.new_call.request_item")

    # This fills out the call window.
    caller_field.send_keys(user)
    call_type.send_keys('r')
    contact_type.send_keys('p')
    req_item.send_keys('CCC Re-provisioning Goodlink')
    if phone in 'iphone':
        long_desc.send_keys('User needs iPhone activation code.')
    if phone in 'android':
        long_desc.send_keys('User needs Android activation code.')
    time.sleep(1.5)
    submit_call.click()

    # This fills out the workflow form.
    phones = driver.find_elements_by_css_selector("#IO\\3a 9e2e453bc8d9b100d65d8061e217d92d")
    unique_id = driver.find_element_by_id("IO:35b7852140ac3100f9474a0ce60d98b3")
    order_now = driver.find_element_by_id("order_now")
    if phone in 'iphone':
        iphone = phones[1]
        iphone.click()
    if phone in 'android':
        android = phones[0]
        android.click()
    unique_id.click()
    order_now.click()

    # This confirms the order.
    confirm_order = driver.find_element_by_id("header_button_checkout_in_footer")
    confirm_order.click()

    # This drills into the REQ
    request = driver.find_element_by_id("requesturl")
    request.click()

    # This drills into the RITM
    request_item = driver.find_element_by_class_name("formlink")
    request_item.click()

    # This drills into the TASK
    task = driver.find_element_by_class_name("formlink")
    task.click()

    # Now we fill out and close the task.
    work_notes = driver.find_element_by_id("sc_task.work_notes")
    close_task = driver.find_element_by_id("79cc847bc611227d01a8092813683b36")
    work_notes.send_keys("Logged into Good Mobile Control.\n"
                         "Added cell phone to user's account.\n"
                         "Verified user received the email.")
    close_task.click()

    close_driver(driver)


def be_defender_reprovision(user, phone, urls):
    """
    This is a Defender reprovision
    """
    caller_field, call_type, contact_type, short_desc, long_desc, submit_call, driver = get_call_fields(urls)
    req_item = driver.find_element_by_id("sys_display.new_call.request_item")

    # This fills out the call window.
    caller_field.send_keys(user)
    call_type.send_keys('r')
    contact_type.send_keys('p')
    req_item.send_keys('*Defender')
    time.sleep(.7)
    req_item.send_keys(Keys.ARROW_DOWN)
    time.sleep(.2)
    req_item.send_keys(Keys.ENTER)

    if phone in 'iphone':
        long_desc.send_keys('User needs iPhone activation code.')
    if phone in 'android':
        long_desc.send_keys('User needs Android activation code.')
    time.sleep(1.5)
    submit_call.click()

    # This fills out the workflow form.
    phones = driver.find_elements_by_css_selector("#IO\\3a 9e2e453bc8d9b100d65d8061e217d92d")
    unique_id = driver.find_element_by_id("IO:35b7852140ac3100f9474a0ce60d98b3")
    desription = driver.find_element_by_id("IO:9cb42a9765dc71001be82f336cc30ab9")
    order_now = driver.find_element_by_id("order_now")
    if phone in 'iphone':
        iphone = phones[1]
        iphone.click()
    if phone in 'android':
        android = phones[0]
        android.click()
    unique_id.click()
    order_now.click()

    # This confirms the order.
    confirm_order = driver.find_element_by_id("header_button_checkout_in_footer")
    confirm_order.click()

    # This drills into the REQ
    request = driver.find_element_by_id("requesturl")
    request.click()

    # This drills into the RITM
    request_item = driver.find_element_by_class_name("formlink")
    request_item.click()

    # This drills into the TASK
    task = driver.find_element_by_class_name("formlink")
    task.click()

    # Now we fill out and close the task.
    work_notes = driver.find_element_by_id("sc_task.work_notes")
    close_task = driver.find_element_by_id("79cc847bc611227d01a8092813683b36")
    work_notes.send_keys("Logged into NTE293\n"
                         "Reprogrammed user's defender assignment.\n"
                         "Emailed user the activation code.")
    close_task.click()

    close_driver(driver)
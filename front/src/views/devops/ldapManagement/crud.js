export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      width: 110,
      view: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Retrieve')
        }
      },
      edit: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      },
      custom: [
        {
          thin: true,
          text: '密码重置',
          size: 'small',
          type: 'warning',
          icon: 'el-icon-refresh-left',
          show () {
            return vm.hasPermissions('ResetLdapUserPassword')
          },
          emit: 'ResetLdapUserPassword'
        }
      ]
    },
    viewOptions: {
      componentType: 'form'
    },
    formOptions: {
      defaultSpan: 12 // 默认的表单 span
    },
    indexRow: { // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 20
    },
    columns: [
      {
        title: '用户名',
        key: 'uid',
        search: {
          disabled: false,
          placeholder: '123'
        },
        width: 60,
        type: 'input',
        form: {
          itemProps: {
            class: { yxtInput: true }
          },
          component: {
            placeholder: ''
          },
          disabled: true
        }
      },
      {
        title: '姓',
        key: 'givenname',
        search: {
          disabled: true
        },
        form: {
          rules: [ // 表单校验规则
            {
              required: true,
              message: '必填项'
            }
          ],
          component: {
            placeholder: '请输入姓'
          }
        },
        width: 40
      },
      {
        title: '名',
        key: 'sn',
        search: {
          disabled: true
        },
        form: {
          rules: [ // 表单校验规则
            {
              required: true,
              message: '必填项'
            }
          ],
          component: {
            placeholder: '请输入名'
          }
        },
        width: 40
      },
      {
        title: 'Email',
        key: 'mail',
        search: {
          disabled: true
        },
        form: {
          rules: [ // 表单校验规则
            {
              required: true,
              message: '必填项'
            }
          ],
          component: {
            placeholder: '请输入email'
          }
        },
        width: 80
      },
      {
        title: '密码',
        key: 'password',
        width: 145,
        type: 'input',
        form: {
          // show: true,
          component: {
            span: 12,
            showPassword: true,
            placeholder: '如为空则自动创建密码'
          },
          editDisabled: false,
          itemProps: {
            class: { yxtInput: true }
          }
        },
        disabled: true
      }
    ]
  }
}

import { request } from '@/api/service'

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    searchOptions: {
      valueChange: true // 搜索框开启valueChange
    },
    options: {
      height: '100%',
      width: '80%',
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      width: 240,
      fixed: 'right',
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
        disabled (index, row) {
          // return row.task_type === '系统任务' || !vm.hasPermissions('Update')
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
          text: '执行',
          size: 'small',
          type: 'primary',
          // icon: 'el-icon-refresh-left',
          show () {
            return vm.hasPermissions('RunTasks')
          },
          emit: 'runTasks'
        },
        {
          thin: true,
          text: '执行结果',
          size: 'small',
          type: 'primary',
          // icon: 'el-icon-refresh-left',
          show () {
            return vm.hasPermissions('TasksResults')
          },
          emit: 'TasksResults'
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
      width: 60
    },
    columns: [
      {
        title: 'ID',
        key: 'id',
        disabled: true,
        form: {
          disabled: true
        }
      },
      {
        title: '名称',
        key: 'name',
        minWidth: 100,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('name')
        },
        form: {
          rules: [ // 表单校验规则
            {
              required: true,
              message: '必填项'
            }
          ],
          show: false,
          component: {
            span: 12,
            placeholder: '请输入任务名称'
          }
        }
      },
      {
        title: '任务类型',
        key: 'task_type',
        width: 100,
        type: 'select',
        search: {
          disabled: false
        },
        dict: {
          // data: vm.dictionary('task_type')
          url: '/api/celery/task/get_task_type/',
          value: 'task_type',
          label: 'task_type'
        },
        form: {
          rules: [ // 表单校验规则
            {
              required: true,
              message: '必填项'
            }
          ],
          // show: false,
          component: {
            span: 12,
            placeholder: '请输入任务名称',
            props: {
              dict: {
                cache: false
              },
              onChange: (value) => {
                console.log('-----你选择了', value)
              }
            }
          },
          valueChange (key, value, form, { getColumn, mode, component, immediate, getComponent }) {
            console.log('-----你选择了', value)
          }
        }
      },
      {
        title: '执行命令类型',
        key: 'command_type',
        disabled: true,
        search: {
          disabled: true
        },
        width: 70,
        type: 'radio',
        dict: {
          data: [
            { value: 'shell', label: 'Shell' },
            { value: 'python', label: 'Python' }
          ]
        },
        form: {
          value: 'shell',
          component: {
            span: 12
          }
        }
      },
      {
        title: '任务执行方法',
        key: 'task',
        width: 145,
        disabled: true,
        type: 'text',
        dict: {
          data: vm.dictionary('task')
        },
        form: {
          show: true,
          component: {
            span: 20
          }
        }
      },
      {
        title: '执行命令',
        key: 'command',
        width: 145,
        disabled: true,
        type: 'text-area',
        dict: {
          data: vm.dictionary('command')
        },
        form: {
          show: false,
          component: {
            span: 20,
            show (context) {
              const { form } = context
              if (form.task === 'remote_job') {
                return false
              } else {
                return true
              }
            },
            style: {
              backgroundColor: '#1e1e1e', // 设置黑色背景，模拟终端效果
              color: '#dcdcdc', // 设置文字颜色为浅灰色
              fontFamily: 'monospace', // 使用等宽字体，增强命令行效果
              // padding: '10px', // 增加内边距，使输入框看起来更像终端
              borderRadius: '4px', // 设置圆角，使外观更现代
              border: '1px solid #1e1e1e'
            }
          }
        }
      },
      {
        title: '选择主机',
        key: 'select_instance',
        disabled: true,
        minWidth: 130,
        search: {
          disabled: true
        },
        // width: 145,
        type: 'table-selector',
        dict: {
          cache: false,
          // url: '/api/cmdb/server_instance/',
          url: '/api/cmdb/server_instance/get_instance_simple/',
          value: 'instancename',
          label: 'instancename',
          getData: (url, dict, {
            form,
            component
          }) => {
            return request({
              url: url
              // params: {
              //   page: 1,
              //   limit: 10
              // }
            }).then(ret => {
              // component._elProps.page = ret.data.page
              // component._elProps.limit = ret.data.limit
              // component._elProps.total = ret.data.total
              return ret.data.data
            })
          }
        },
        form: {
          // show: false,
          itemProps: {
            class: { yxtInput: true }
          },
          component: {
            span: 12,
            // pagination: true,
            props: { multiple: true },
            elProps: {
              columns: [
                {
                  field: 'instanceid',
                  title: '实例id'
                },
                {
                  field: 'instancename',
                  title: '实例名称'
                }
              ]
            }
          }
        }
      },
      {
        title: '启用状态',
        key: 'enabled',
        search: {
          disabled: false
        },
        width: 70,
        type: 'radio',
        dict: {
          data: vm.dictionary('button_status_bool')
        },
        form: {
          rules: [ // 表单校验规则
            {
              required: true,
              message: '必填项'
            }
          ],
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '任务调度时间',
        key: 'crontab',
        width: 145,
        dict: {
          data: vm.dictionary('crontab')
        },
        form: {
          show: false,
          component: {
            span: 12,
            placeholder: '请输入cronta时间，* * * * *'
          },
          helper: 'crontab时间配置, 例如 10 * * * * 表示每小时的第10分钟执行'
        }
      },
      {
        title: '描述',
        key: 'description',
        type: 'text-area',
        minWidth: 145,
        dict: {
          data: vm.dictionary('description')
        },
        form: {
          rules: [ // 表单校验规则
            {
              required: true,
              message: '必填项'
            }
          ],
          show: false,
          component: {
            span: 20
          }
        }
      },
      {
        title: '最后一次运行时间',
        key: 'last_run_at',
        width: 145,
        dict: {
          data: vm.dictionary('last_run_at')
        },
        form: {
          show: true,
          disabled: true,
          component: {
            span: 12
          }
        }
      },
      {
        title: '运行次数',
        key: 'total_run_count',
        width: 80,
        dict: {
          data: vm.dictionary('total_run_count')
        },
        form: {
          show: false,
          disabled: true,
          component: {
            span: 12
          }
        }
      }
    ],
    formGroup: {
      type: 'collapse', // tab
      accordion: false,
      groups: {
        base: {
          title: '任务信息',
          icon: 'el-icon-goods',
          collapsed: false,
          columns: ['name', 'task_type', 'description']
        },
        task_run_method: {
          title: '任务运行方法',
          icon: 'el-icon-price-tag',
          collapsed: false,
          columns: ['task'],
          show (context) {
            const { form } = context
            if (form.task_type === '系统任务') {
              return true
            } else {
              return false
            }
          }
        },
        command: {
          title: '执行命令',
          icon: 'el-icon-price-tag',
          collapsed: false,
          columns: ['command_type', 'command'],
          show (context) {
            const { form } = context
            if (form.task_type === '系统任务') {
              return false
            } else {
              return true
            }
          }
        },
        instance: {
          title: '选择主机',
          collapsed: false,
          icon: 'el-icon-warning-outline',
          columns: ['select_instance'],
          show (context) {
            const { form } = context
            if (form.task_type === '远程任务') {
              return true
            } else {
              return false
            }
          }
        },
        crontab: {
          title: '调度时间配置',
          collapsed: false,
          icon: 'el-icon-warning-outline',
          columns: ['crontab', 'enabled']
          // show (context) {
          //   const { form } = context
          //   if (form.task_type === '系统任务') {
          //     return false
          //   } else {
          //     return true
          //   }
          // }
        }
        // custom: {
        //   title: '自定义',
        //   collapsed: false,
        //   show (context) {
        //     console.log('custom context', context)
        //     return context.mode === 'view'
        //   },
        //   disabled: false,
        //   icon: 'el-icon-warning-outline',
        //   columns: ['custom', 'custom2']
        // }
      }
    }
  }
}

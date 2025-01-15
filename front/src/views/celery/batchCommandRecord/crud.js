// import { request } from '@/api/service'

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
        show: false,
        text: '',
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        show: false,
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      },
      custom: [
        {
          thin: true,
          text: '结果查看',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-video-camera-solid',
          show () {
            return vm.hasPermissions('batchCommandResult')
          },
          emit: 'batchCommandResult'
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
        title: '执行人',
        key: 'executor_name',
        width: 145,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('executor_name')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '执行的命令',
        key: 'command',
        width: 145,
        showOverflowTooltip: true,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('command')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '执行时间',
        key: 'execution_time',
        width: 145,
        dict: {
          data: vm.dictionary('execution_time')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '执行状态',
        key: 'status',
        width: 145,
        dict: {
          data: vm.dictionary('status')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '执行结果',
        key: 'formatted_output',
        minWidth: 145,
        show: false,
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      }
    ]
  }
}
